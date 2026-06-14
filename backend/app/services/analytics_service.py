"""
Analytics & Dashboard Service.
"""

from decimal import Decimal
import datetime
from sqlalchemy import select, func, and_, desc, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

from app.models.customers import TelecomCustomer
from app.models.ml import ChurnPrediction
from app.models.campaigns import CampaignResult
from app.repositories.campaign_repo import CampaignRepository
from app.schemas.dashboard import (
    DashboardKPIResponse, ChurnTrendPoint, DashboardChurnTrendsResponse,
    RevenueRiskPoint, DashboardRevenueRiskResponse,
    RegionalAnalysisPoint, DashboardRegionalResponse,
    OperatorAnalysisPoint, DashboardOperatorResponse
)


class AnalyticsService:
    """Computes high-level business intelligence queries and data aggregates for dashboards."""

    def __init__(self, db: AsyncSession, campaign_repo: CampaignRepository) -> None:
        self.db = db
        self.campaign_repo = campaign_repo

    async def _get_latest_prediction_subquery(self):
        """Constructs subquery for the latest prediction per customer."""
        return (
            select(
                ChurnPrediction.customer_id,
                ChurnPrediction.churn_probability,
                ChurnPrediction.risk_category,
                func.row_number()
                .over(
                    partition_by=ChurnPrediction.customer_id,
                    order_by=desc(ChurnPrediction.prediction_date),
                )
                .label("rn"),
            )
            .subquery()
        )

    async def get_dashboard_kpis(self) -> DashboardKPIResponse:
        """Fetch general KPIs: total/active customer counts, average risk, total revenue at risk, campaign conversion rates."""
        # 1. Total & Active customers count
        stmt_counts = select(
            func.count(TelecomCustomer.id),
            func.count(func.nullif(TelecomCustomer.status != "active", True))
        )
        res_counts = await self.db.execute(stmt_counts)
        total_cust, active_cust = res_counts.fetchone() or (0, 0)

        # 2. Average Churn Probability & Revenue at Risk
        subq = await self._get_latest_prediction_subquery()
        stmt_risk = (
            select(
                func.avg(subq.c.churn_probability),
                func.sum(TelecomCustomer.arpu)
            )
            .join(subq, and_(subq.c.customer_id == TelecomCustomer.id, subq.c.rn == 1))
            .where(TelecomCustomer.status == "active")
        )
        res_risk = await self.db.execute(stmt_risk)
        avg_prob, total_arpu = res_risk.fetchone() or (0.0, Decimal("0.00"))
        
        # Calculate revenue at risk (sum of ARPU for high-risk customers)
        stmt_rev_at_risk = (
            select(func.sum(TelecomCustomer.arpu))
            .join(subq, and_(subq.c.customer_id == TelecomCustomer.id, subq.c.rn == 1))
            .where(and_(TelecomCustomer.status == "active", subq.c.risk_category == "HIGH"))
        )
        res_rev_at_risk = await self.db.execute(stmt_rev_at_risk)
        revenue_at_risk = res_rev_at_risk.scalar() or Decimal("0.00")

        # 3. Active Campaigns count
        active_campaigns = await self.campaign_repo.get_active_campaigns_count()

        # 4. Campaign conversion rate (total conversions / total targets)
        stmt_campaign_totals = select(
            func.sum(CampaignResult.total_targets),
            func.sum(CampaignResult.conversions)
        )
        res_campaigns = await self.db.execute(stmt_campaign_totals)
        total_targets, conversions = res_campaigns.fetchone() or (0, 0)
        
        conversion_rate = 0.0
        if total_targets and total_targets > 0:
            conversion_rate = float(conversions) / float(total_targets)

        return DashboardKPIResponse(
            total_customers=total_cust,
            active_customers=active_cust,
            average_churn_probability=float(avg_prob) if avg_prob else 0.0,
            revenue_at_risk=revenue_at_risk,
            active_campaigns_count=active_campaigns,
            campaign_conversion_rate=conversion_rate,
        )

    async def get_churn_trends(self) -> DashboardChurnTrendsResponse:
        """Fetch monthly churn aggregates."""
        # Use strftime for SQLite, to_char for PostgreSQL
        if settings.DATABASE_URL.startswith("sqlite"):
            month_expr = func.strftime("%Y-%m", ChurnPrediction.prediction_date)
        else:
            month_expr = func.to_char(ChurnPrediction.prediction_date, "YYYY-MM")

        stmt = (
            select(
                month_expr.label("month"),
                func.avg(ChurnPrediction.churn_probability),
                func.count(func.nullif(ChurnPrediction.risk_category != "HIGH", True))
            )
            .group_by("month")
            .order_by("month")
            .limit(12)
        )
        result = await self.db.execute(stmt)
        
        trends = []
        for period, avg_prob, high_risk_count in result.fetchall():
            trends.append(
                ChurnTrendPoint(
                    period=period,
                    average_churn_probability=float(avg_prob),
                    predicted_churn_count=high_risk_count
                )
            )

        return DashboardChurnTrendsResponse(trends=trends)

    async def get_revenue_risk_customers(self) -> DashboardRevenueRiskResponse:
        """Fetch list of top customers contributing to revenue risk."""
        subq = await self._get_latest_prediction_subquery()
        stmt = (
            select(
                TelecomCustomer.id,
                TelecomCustomer.customer_id,
                TelecomCustomer.full_name,
                TelecomCustomer.arpu,
                subq.c.churn_probability,
                subq.c.risk_category
            )
            .join(subq, and_(subq.c.customer_id == TelecomCustomer.id, subq.c.rn == 1))
            .where(TelecomCustomer.status == "active")
            .order_by(desc(TelecomCustomer.arpu * subq.c.churn_probability))
            .limit(10)
        )
        result = await self.db.execute(stmt)
        
        risk_list = []
        for pk, cust_id, name, arpu, prob, cat in result.fetchall():
            arpu_val = arpu or Decimal("0.00")
            prob_val = float(prob) if prob else 0.0
            risk_list.append(
                RevenueRiskPoint(
                    customer_uuid=pk,
                    customer_id=cust_id,
                    full_name=name,
                    arpu=arpu_val,
                    churn_probability=prob_val,
                    risk_level=cat,
                    revenue_at_risk=arpu_val * Decimal(str(prob_val))
                )
            )

        return DashboardRevenueRiskResponse(high_risk_customers=risk_list)

    async def get_regional_analysis(self) -> DashboardRegionalResponse:
        """Fetch regional churn statistics breaks."""
        subq = await self._get_latest_prediction_subquery()
        stmt = (
            select(
                TelecomCustomer.region,
                func.count(TelecomCustomer.id),
                func.count(func.nullif(subq.c.risk_category != "HIGH", True)),
                func.avg(subq.c.churn_probability),
                func.sum(TelecomCustomer.arpu)
            )
            .join(subq, and_(subq.c.customer_id == TelecomCustomer.id, subq.c.rn == 1), isouter=True)
            .group_by(TelecomCustomer.region)
            .order_by(desc(func.count(TelecomCustomer.id)))
        )
        result = await self.db.execute(stmt)
        
        regions = []
        for region, total, churned, avg_prob, sum_arpu in result.fetchall():
            if not region:
                continue
            arpu_val = sum_arpu or Decimal("0.00")
            prob_val = float(avg_prob) if avg_prob else 0.0
            regions.append(
                RegionalAnalysisPoint(
                    region=region,
                    customer_count=total,
                    churn_count=churned,
                    average_churn_probability=prob_val,
                    revenue_at_risk=arpu_val * Decimal(str(prob_val))
                )
            )

        return DashboardRegionalResponse(regions=regions)

    async def get_operator_analysis(self) -> DashboardOperatorResponse:
        """Fetch churn comparison metrics across operators."""
        subq = await self._get_latest_prediction_subquery()
        stmt = (
            select(
                TelecomCustomer.operator,
                func.count(TelecomCustomer.id),
                func.count(func.nullif(subq.c.risk_category != "HIGH", True)),
                func.avg(subq.c.churn_probability),
                func.sum(TelecomCustomer.arpu)
            )
            .join(subq, and_(subq.c.customer_id == TelecomCustomer.id, subq.c.rn == 1), isouter=True)
            .group_by(TelecomCustomer.operator)
            .order_by(desc(func.count(TelecomCustomer.id)))
        )
        result = await self.db.execute(stmt)
        
        operators = []
        for operator, total, churned, avg_prob, sum_arpu in result.fetchall():
            if not operator:
                continue
            arpu_val = sum_arpu or Decimal("0.00")
            prob_val = float(avg_prob) if avg_prob else 0.0
            operators.append(
                OperatorAnalysisPoint(
                    operator=operator,
                    customer_count=total,
                    churn_count=churned,
                    average_churn_probability=prob_val,
                    revenue_at_risk=arpu_val * Decimal(str(prob_val))
                )
            )

        return DashboardOperatorResponse(operators=operators)

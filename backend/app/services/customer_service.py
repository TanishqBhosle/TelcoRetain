"""
Customer Service.
"""

import uuid
from typing import List, Optional, Tuple

from app.exceptions.custom import CustomerNotFoundError, ConflictError
from app.models.customers import TelecomCustomer
from app.repositories.customer_repo import CustomerRepository
from app.schemas.customers import TelecomCustomerCreate, TelecomCustomerUpdate


class CustomerService:
    """Manages telecom customer master registry operations."""

    def __init__(self, customer_repo: CustomerRepository) -> None:
        self.customer_repo = customer_repo

    async def get_customer(self, customer_uuid: uuid.UUID) -> TelecomCustomer:
        """Fetch a single customer details by UUID primary key."""
        customer = await self.customer_repo.get_by_id(customer_uuid)
        if not customer:
            raise CustomerNotFoundError(customer_uuid)
        return customer

    async def get_customer_by_id_string(self, customer_id: str) -> TelecomCustomer:
        """Fetch a single customer by their operator-assigned string ID (e.g. CUST001)."""
        customer = await self.customer_repo.get_by_customer_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)
        return customer

    async def create_customer(self, req: TelecomCustomerCreate) -> TelecomCustomer:
        """Register a new customer profile."""
        existing = await self.customer_repo.get_by_customer_id(req.customer_id)
        if existing:
            raise ConflictError(f"Customer with ID '{req.customer_id}' already registered")

        customer = TelecomCustomer(
            customer_id=req.customer_id,
            full_name=req.full_name,
            email=req.email,
            phone_number=req.phone_number,
            gender=req.gender,
            age=req.age,
            region=req.region,
            operator=req.operator,
            join_date=req.join_date,
            contract_type=req.contract_type,
            paperless_billing=req.paperless_billing,
            payment_method=req.payment_method,
            monthly_charges=req.monthly_charges,
            total_charges=req.total_charges,
            tenure_months=req.tenure_months,
            arpu=req.arpu,
            churn_status=req.churn_status,
            status=req.status,
        )
        return await self.customer_repo.create(customer)

    async def update_customer(self, customer_uuid: uuid.UUID, req: TelecomCustomerUpdate) -> TelecomCustomer:
        """Update existing customer details."""
        customer = await self.get_customer(customer_uuid)

        update_data = req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(customer, key, value)

        return await self.customer_repo.update(customer)

    async def list_customers(
        self,
        page: int = 1,
        limit: int = 20,
        operator: Optional[str] = None,
        region: Optional[str] = None,
        risk_level: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[TelecomCustomer], int]:
        """Fetch paginated customer listing based on filtering query params."""
        skip = (page - 1) * limit
        return await self.customer_repo.list_customers(
            skip=skip,
            limit=limit,
            operator=operator,
            region=region,
            risk_level=risk_level,
            search=search,
        )

    async def get_customer_timeline(self, customer_uuid: uuid.UUID) -> List[dict]:
        """Fetch chronological timeline events (recharges, support tickets, prediction logs)."""
        # Ensure customer exists
        await self.get_customer(customer_uuid)
        return await self.customer_repo.get_timeline(customer_uuid)

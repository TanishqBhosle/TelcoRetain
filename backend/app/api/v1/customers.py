"""
Customers API Router.
"""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_db, get_current_user, require_role
from app.repositories.customer_repo import CustomerRepository
from app.repositories.recharge_repo import RechargeHistoryRepository
from app.repositories.support_repo import SupportTicketRepository
from app.repositories.usage_repo import UsageMetricsRepository
from app.services.customer_service import CustomerService
from app.schemas.customers import (
    TelecomCustomerResponse, TelecomCustomerDetailResponse, TelecomCustomerCreate,
    TelecomCustomerUpdate, CustomerTimelineEvent, UsageMetricsResponse,
    CustomerSupportResponse, RechargeHistoryResponse,
)
from app.schemas.common import APIResponse, PaginatedData

router = APIRouter(tags=["Customers"])

BUSINESS_ROLES = ["Super Admin", "Admin", "Retention Manager", "Marketing Manager", "Business Analyst", "Customer Support Executive", "Executive Viewer"]
CUSTOMER_READ_ROLES = ["Super Admin", "Admin", "Retention Manager", "Business Analyst", "Customer Support Executive"]


async def get_customer_service(db=Depends(get_db)) -> CustomerService:
    """Dependency: initializes CustomerService."""
    return CustomerService(CustomerRepository(db))


@router.get("/customers", response_model=APIResponse[PaginatedData[TelecomCustomerResponse]])
async def list_customers(
    page: int = Query(1, ge=1, description="Page index (1-based)"),
    limit: int = Query(20, ge=1, le=100, description="Page size limit"),
    operator: Optional[str] = Query(None, description="Filter by telecom operator"),
    region: Optional[str] = Query(None, description="Filter by customer region"),
    risk_level: Optional[str] = Query(None, description="Filter by latest prediction risk (LOW, MEDIUM, HIGH)"),
    search: Optional[str] = Query(None, description="Search term for names, IDs, phone, email"),
    customer_service: CustomerService = Depends(get_customer_service),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Retrieves a paginated list of customers matching query filters."""
    items, total = await customer_service.list_customers(
        page=page,
        limit=limit,
        operator=operator,
        region=region,
        risk_level=risk_level,
        search=search,
    )
    pages = (total + limit - 1) // limit

    paginated = PaginatedData(
        items=[TelecomCustomerResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )

    return APIResponse(
        success=True,
        message="Customers list retrieved successfully",
        data=paginated,
    )


@router.post("/customers", response_model=APIResponse[TelecomCustomerResponse], status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: TelecomCustomerCreate,
    customer_service: CustomerService = Depends(get_customer_service),
    current_user=Depends(require_role(["Super Admin", "Admin", "Retention Manager"])),
):
    """Registers a new telecom customer master record."""
    customer = await customer_service.create_customer(payload)
    return APIResponse(
        success=True,
        message="Customer record created successfully",
        data=TelecomCustomerResponse.model_validate(customer),
    )


@router.get("/customers/{id}", response_model=APIResponse[TelecomCustomerDetailResponse])
async def get_customer_details(
    id: uuid.UUID,
    customer_service: CustomerService = Depends(get_customer_service),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Fetches details of a single customer, including historical behaviors."""
    customer = await customer_service.get_customer(id)
    return APIResponse(
        success=True,
        message="Customer details retrieved",
        data=TelecomCustomerDetailResponse.model_validate(customer),
    )


@router.put("/customers/{id}", response_model=APIResponse[TelecomCustomerResponse])
async def update_customer(
    id: uuid.UUID,
    payload: TelecomCustomerUpdate,
    customer_service: CustomerService = Depends(get_customer_service),
    current_user=Depends(require_role(["Super Admin", "Admin", "Retention Manager"])),
):
    """Updates properties on a customer master profile."""
    customer = await customer_service.update_customer(id, payload)
    return APIResponse(
        success=True,
        message="Customer record updated successfully",
        data=TelecomCustomerResponse.model_validate(customer),
    )


@router.get("/customers/{id}/timeline", response_model=APIResponse[List[CustomerTimelineEvent]])
async def get_customer_timeline(
    id: uuid.UUID,
    customer_service: CustomerService = Depends(get_customer_service),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Fetches chronological activity events log for a customer."""
    timeline = await customer_service.get_customer_timeline(id)
    events = [CustomerTimelineEvent.model_validate(e) for e in timeline]
    return APIResponse(
        success=True,
        message="Customer activity timeline retrieved",
        data=events,
    )


@router.get("/customers/{id}/usage", response_model=APIResponse[List[UsageMetricsResponse]])
async def get_customer_usage(
    id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Fetches usage history for a customer profile."""
    items = await UsageMetricsRepository(db).get_by_customer_id(id)
    return APIResponse(
        success=True,
        message="Customer usage history retrieved",
        data=[UsageMetricsResponse.model_validate(item) for item in items],
    )


@router.get("/customers/{id}/complaints", response_model=APIResponse[List[CustomerSupportResponse]])
async def get_customer_complaints(
    id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Fetches support tickets and complaints for a customer profile."""
    items = await SupportTicketRepository(db).get_by_customer_id(id)
    return APIResponse(
        success=True,
        message="Customer complaints retrieved",
        data=[CustomerSupportResponse.model_validate(item) for item in items],
    )


@router.get("/customers/{id}/recharge-history", response_model=APIResponse[List[RechargeHistoryResponse]])
async def get_customer_recharge_history(
    id: uuid.UUID,
    db=Depends(get_db),
    current_user=Depends(require_role(CUSTOMER_READ_ROLES)),
):
    """Fetches recharge transaction history for a customer profile."""
    items = await RechargeHistoryRepository(db).get_by_customer_id(id)
    return APIResponse(
        success=True,
        message="Customer recharge history retrieved",
        data=[RechargeHistoryResponse.model_validate(item) for item in items],
    )

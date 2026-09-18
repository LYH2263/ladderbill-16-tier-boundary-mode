from fastapi import APIRouter

from app.schemas.billing import BillRequest, BoundaryCompareRequest, CompareRequest
from app.services.billing_service import BillingService

router = APIRouter(tags=["billing"])


@router.post("/bill")
def post_bill(body: BillRequest):
    with BillingService() as svc:
        return svc.run_bill(body.kwh, body.peak, body.account_id, body.persist)


@router.post("/compare")
def post_compare(body: CompareRequest):
    with BillingService() as svc:
        return svc.run_compare(body.kwh, body.persist)


@router.post("/boundary_compare")
def post_boundary_compare(body: BoundaryCompareRequest):
    """只读：同一探针电量在两种含端模式下的分段与合计，不写运行记录。"""
    with BillingService() as svc:
        return svc.run_boundary_compare(body.kwh)

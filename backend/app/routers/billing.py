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


@router.post("/boundary-compare")
def post_boundary_compare(body: BoundaryCompareRequest):
    """Read-only side-by-side of both boundary modes; never persists a run."""
    with BillingService() as svc:
        return svc.run_boundary_compare(body.kwh, body.peak)

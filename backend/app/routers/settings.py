from fastapi import APIRouter

from app.schemas.billing import BoundaryModeUpdate
from app.services.billing_service import BillingService

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    with BillingService() as svc:
        return svc.settings_map()


@router.put("/settings/boundary_mode")
def put_boundary_mode(body: BoundaryModeUpdate):
    with BillingService() as svc:
        return svc.update_boundary_mode(body.value)

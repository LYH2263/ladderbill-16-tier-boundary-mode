from fastapi import APIRouter, HTTPException

from app.schemas.billing import BoundaryModeRequest
from app.services.billing_service import BillingService

router = APIRouter(tags=["settings"])


@router.get("/settings")
def get_settings():
    with BillingService() as svc:
        return svc.settings_map()


@router.put("/settings/boundary-mode")
def put_boundary_mode(body: BoundaryModeRequest):
    with BillingService() as svc:
        try:
            return svc.set_boundary_mode(body.boundary_mode)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

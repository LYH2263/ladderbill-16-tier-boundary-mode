from pydantic import BaseModel, Field

from app.engines.tier_progressive import BOUNDARY_MODES


class BillRequest(BaseModel):
    account_id: int | None = None
    kwh: float = Field(ge=0)
    peak: bool = False
    persist: bool = True


class CompareRequest(BaseModel):
    kwh: float = Field(ge=0)
    persist: bool = False


class BoundaryCompareRequest(BaseModel):
    kwh: float = Field(ge=0)


class BoundaryModeUpdate(BaseModel):
    value: str = Field(pattern=f"^({'|'.join(BOUNDARY_MODES)})$")


class CalcRunOut(BaseModel):
    id: int
    kind: str
    account_id: int | None
    input_json: str
    result_json: str
    created_at: str

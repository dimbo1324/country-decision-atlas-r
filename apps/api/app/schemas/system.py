from pydantic import BaseModel
from typing import Literal


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready"]
    service: str
    environment: str
    database: Literal["ok"]

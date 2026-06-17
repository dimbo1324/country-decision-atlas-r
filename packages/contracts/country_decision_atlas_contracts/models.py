from pydantic import BaseModel, Field
class HealthResponse(BaseModel):
    status: str = Field(description="Machine-readable service status.")
    service: str = Field(description="Service that produced the response.")
    environment: str = Field(description="Runtime environment name.")

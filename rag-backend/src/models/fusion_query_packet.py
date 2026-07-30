from enum import Enum
from pydantic import BaseModel, Field

class FusionQueryPacket(BaseModel):
    normal: str = Field(description="The reformulated query for the normal variant")
    abstract: str = Field(description="The reformulated query for the abstract variant")
    detailed: str = Field(description="The reformulated query for the detailed variant")

class FusionRAGResponse(BaseModel):
    packets: list[FusionQueryPacket] = Field(
        description="List of 3 dictionary packets. First packet is original, remaining 2 are variations.",
        min_length=3,
        max_length=3
    )
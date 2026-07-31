from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field

from models.enums import InformationTier

class Region(str, Enum):
    NORCAL = "Northern California"
    SOCAL = "Southern California"
    OUT_OF_STATE = "Outside California"
    REMOTE = "Remote"

class StartTimeframe(str, Enum):
    ASAP = "As soon as possible"
    SUMMER = "Starting during summer"
    WINTER = "Starting during winter"

class ActivityMetadata(BaseModel):
    region: Region = Field(
        default=Region.REMOTE,
        description="Categorize the primary region where the activity takes place. Northern CA includes Sacramento, Bay Area, etc."
    )
    timeframe: StartTimeframe = Field(
        default=StartTimeframe.ASAP,
        description="Categorize the starting timeframe for the activity that falls either in the summer half of the year or the winter half."
    )

    def to_chromadb_metadata(self):
        flat_metadata = {}
        for key, value in self.model_dump().items():
            if value is None:
                # None is not supported by chromadb
                flat_metadata[key] = ""
            else:
                flat_metadata[key] = value

        return flat_metadata

    def to_where_condition(self) -> Optional[dict[str, Any]]:
        data = self.model_dump()
        conditions = []

        for key, value in data.items():
            if value is not None and value != "":
                conditions.append({key: {"$eq": value}})

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}

class Activity(BaseModel):
    id: str
    text_variations: dict[InformationTier, str]
    soft_skills: list[str]
    metadata: ActivityMetadata
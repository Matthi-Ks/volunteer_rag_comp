from typing import Optional
from pydantic import BaseModel, Field

from models.enums import InformationTier


class ActivityMetadata(BaseModel):
    location: str = Field(
        description="The city, country, or specific location of the organization. If remote or not mentioned, set to 'Remote'."
    )
    starting_date: str = Field(
        description="The starting date or timeframe. If not mentioned, strictly set to 'As soon as possible'."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="The end date of the activity if mentioned, otherwise None."
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

class Activity(BaseModel):
    id: str
    text_variations: dict[InformationTier, str]
    soft_skills: list[str]
    metadata: ActivityMetadata
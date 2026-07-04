from typing import Optional
from pydantic import BaseModel, Field


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

class TextVariations(BaseModel):
    title_only: str
    title_softskill: str
    title_desc: str
    title_desc_softskill: str

class Activity(BaseModel):
    id: str
    text_variations: TextVariations
    soft_skills: list[str]
    metadata: ActivityMetadata

class SPOTriple(BaseModel):
    subject: str = Field(..., description="the main entity")
    predicate: str = Field(..., description="the relationship")
    object: str = Field(..., description="the related entity")
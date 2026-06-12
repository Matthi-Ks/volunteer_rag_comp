from pydantic import BaseModel, Field

class Metadata(BaseModel):
    location: str = Field("Remote", description="The city or region mentioned in the text. Return None if not found.")
    timeframe: str = Field(None, description="The time period or starting time mentioned in the text (e.g. starting June, during Summer, etc). Return None if not found.")

class MetadataExtractor:
    test = ""
import instructor
from pydantic import BaseModel, Field
from typing import Optional

class Metadata(BaseModel):
    location: str = Field(
        description="The city, country, or specific location of the organization. If remote or not mentioned, set to 'Remote'."
    )
    start_time: str = Field(
        description="The starting date or timeframe. If not mentioned, strictly set to 'As soon as possible'."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="The end date of the activity if mentioned, otherwise None."
    )

client = instructor.from_provider(
    "ollama/ministral-3:8b",
    base_url="http://localhost:11434/v1",
    mode=instructor.Mode.JSON,
)


def extract_metadata(desc: str) -> Metadata:
    prompt = f"Extract the location and time related metadata from the following text:\n\n{desc}"

    response = client.chat.completions.create(
        model="ministral-3:8b",
        messages = [
            {
                "role": "system",
                "content": "You are a precise data extraction assistant. Analyze the text carefully and extract the requested fields."
            },
            {"role": "user", "content": prompt},
        ],
        response_model=Metadata
    )

    return response
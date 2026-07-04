import instructor

from pipelines.data.util.config_loader import load_config
from pipelines.data.models.activity import ActivityMetadata

config = load_config()

client = instructor.from_provider(
    "ollama/"+config["ollama"]["model"],
    base_url=config["ollama"]["url"],
    mode=instructor.Mode.JSON,
)


def extract_metadata(desc: str) -> ActivityMetadata:
    prompt = f"Extract the location and time related metadata from the following text:\n\n{desc}"

    response = client.chat.completions.create(
        model = config["ollama"]["model"],
        messages = [
            {
                "role": "system",
                "content": "You are a precise data extraction assistant. Analyze the text carefully and extract the requested fields."
            },
            {"role": "user", "content": prompt},
        ],
        response_model = ActivityMetadata
    )

    return response
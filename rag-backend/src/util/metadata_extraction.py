from util.config_loader import load_config
from models.activity import ActivityMetadata
from util.llm_factory import LLMFactory

config = load_config()

def extract_metadata(desc: str) -> ActivityMetadata:
    prompt = f"Extract the location and timeframe related metadata from the following text:\n\n{desc}"

    client = LLMFactory.get_instructor_wrapping()
    model_name = config["ollama"]["model"] if config["use_local_llm"] else config["mistral"]["model"]

    try:
        return client.chat.completions.create(
            model = model_name,
            messages = [
                {
                    "role": "system",
                    "content": "You are a precise data extraction assistant. Analyze the text carefully and extract the requested fields."
                },
                {"role": "user", "content": prompt},
            ],
            response_model = ActivityMetadata
        )
    except Exception as e:
        # fallback
        return ActivityMetadata()
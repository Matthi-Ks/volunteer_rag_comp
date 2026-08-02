from pydantic import BaseModel

class Profile(BaseModel):
    id: int
    esco_skills: list[str]
    biography: str
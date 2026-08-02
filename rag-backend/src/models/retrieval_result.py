from pydantic import BaseModel
from transformers.image_transforms import to_pil_image

from models.enums import QuestionVariant


class ResultScore(BaseModel):
    vector_dist: float | None
    bm25_score: float | None
    rrf: float | None

class RetrievalResult(BaseModel):
    id: str
    text: str
    origin_variation: QuestionVariant
    scores: ResultScore
    associated_skills: list[str]

    @staticmethod
    def from_chroma_results(chromadb_results, variations: list[QuestionVariant]) -> list["RetrievalResult"]:
        mapped: list[RetrievalResult] = []

        for i, variation in enumerate(variations):
            for j in range(len(chromadb_results['ids'][i])):
                mapped.append(RetrievalResult(
                    id=chromadb_results['ids'][i][j],
                    text=chromadb_results['documents'][i][j],
                    origin_variation=variation,
                    scores=ResultScore(
                        vector_dist=chromadb_results['distances'][i][j],
                        bm25_score=None,
                        rrf=None
                    ),
                    associated_skills=chromadb_results['metadatas'][i][j].get("esco_skills", [])
                ))

        return mapped

    @staticmethod
    def from_bm25_results(bm25_results, variations: list[QuestionVariant]) -> list["RetrievalResult"]:
        mapped: list[RetrievalResult] = []

        for i, variation in enumerate(variations):
            for doc_id, doc_text, score, skills in bm25_results[i]:
                mapped.append(RetrievalResult(
                    id=doc_id,
                    text=doc_text,
                    origin_variation=variation,
                    scores=ResultScore(
                        vector_dist=None,
                        bm25_score=score,
                        rrf=None
                    ),
                    associated_skills=skills
                ))

        return mapped

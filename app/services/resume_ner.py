from transformers import pipeline

from app.core.config import settings


class ResumeNER:
    """Named Entity Recognition service for CV parsing."""

    def __init__(self):
        self.pipeline = pipeline(
            "token-classification",
            model=settings.model_name,
            aggregation_strategy="simple",
        )

    def extract(self, text: str) -> list[dict]:
        """Extract entities from resume text."""

        if not text.strip():
            return []

        entities = self.pipeline(text)

        return [
            {
                "text": entity["word"],
                "label": entity["entity_group"],
                "score": round(float(entity["score"]), 4),
                "start": entity["start"],
                "end": entity["end"],
            }
            for entity in entities
        ]
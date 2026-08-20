from sentence_transformers import SentenceTransformer


class SemanticSimilarityService:
    MODEL_NAME = "intfloat/multilingual-e5-small"

    def __init__(self) -> None:
        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

    def similarity(
        self,
        query: str,
        document: str,
    ) -> float:
        if not query.strip() or not document.strip():
            return 0.0

        embeddings = self.model.encode(
            [
                f"query: {query}",
                f"passage: {document}",
            ],
            normalize_embeddings=True,
        )

        query_embedding = embeddings[0]
        document_embedding = embeddings[1]

        score = float(
            query_embedding
            @ document_embedding
        )

        return round(score, 4)
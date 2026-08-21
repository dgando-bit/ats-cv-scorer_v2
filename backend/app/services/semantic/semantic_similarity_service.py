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

        return self.similarities(
            query=query,
            documents=[document],
        )[0]

    def similarities(
        self,
        query: str,
        documents: list[str],
    ) -> list[float]:
        if not documents:
            return []

        if not query.strip():
            return [
                0.0
                for _ in documents
            ]

        prepared = [
            f"query: {query}",
            *[
                (
                    f"passage: {document}"
                    if document.strip()
                    else "passage:"
                )
                for document in documents
            ],
        ]

        embeddings = self.model.encode(
            prepared,
            normalize_embeddings=True,
        )

        query_embedding = embeddings[0]
        document_embeddings = embeddings[1:]

        scores = (
            document_embeddings
            @ query_embedding
        )

        return [
            round(
                float(score),
                4,
            )
            for score in scores
        ]
from sentence_transformers import CrossEncoder


class JobReranker:
    MODEL_NAME = (
        "cross-encoder/"
        "mmarco-mMiniLMv2-L12-H384-v1"
    )

    def __init__(self) -> None:
        self.model = CrossEncoder(
            self.MODEL_NAME,
            max_length=512,
        )

    def score(
        self,
        query: str,
        document: str,
    ) -> float:
        if not query.strip() or not document.strip():
            return 0.0

        scores = self.model.predict(
            [(query, document)]
        )

        return float(scores[0])

    def rank(
        self,
        query: str,
        documents: list[str],
    ) -> list[tuple[int, float]]:
        if not query.strip() or not documents:
            return []

        pairs = [
            (query, document)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranking = sorted(
            enumerate(scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (index, float(score))
            for index, score in ranking
        ]
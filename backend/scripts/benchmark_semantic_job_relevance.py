# 1. Imports
from dataclasses import dataclass

import numpy as np

from app.models.job import JobOffer
from app.services.semantic.semantic_job_relevance_scorer import (
    SemanticJobRelevanceScorer,
)

# 2. Classes utilisées uniquement par le benchmark

@dataclass
class BenchmarkItem:
    job: JobOffer
    relevance: int


@dataclass
class BenchmarkCase:
    query: str
    items: list[BenchmarkItem]

# 3. Dataset du benchmark
BENCHMARK = [
    BenchmarkCase(
        query="développeur backend",
        items=[
            BenchmarkItem(
                JobOffer(
                    title="Software Engineer",
                    description=(
                        "Conception d'APIs REST, "
                        "microservices et services côté serveur."
                    ),
                    skills=[
                        "Python",
                        "FastAPI",
                        "PostgreSQL",
                        "REST API",
                    ],
                ),
                3,
            ),
            BenchmarkItem(
                JobOffer(
                    title="Ingénieur logiciel",
                    description=(
                        "Développement de microservices "
                        "et systèmes distribués."
                    ),
                    skills=[
                        "Python",
                        "PostgreSQL",
                        "Docker",
                    ],
                ),
                3,
            ),
            BenchmarkItem(
                JobOffer(
                    title="Frontend Engineer",
                    description=(
                        "Développement d'interfaces web "
                        "et d'applications frontend."
                    ),
                    skills=[
                        "React",
                        "TypeScript",
                        "CSS",
                    ],
                ),
                1,
            ),
            BenchmarkItem(
                JobOffer(
                    title="DevOps Engineer",
                    description=(
                        "Automatisation CI/CD, Kubernetes "
                        "et infrastructure cloud."
                    ),
                    skills=[
                        "Docker",
                        "Kubernetes",
                        "Terraform",
                    ],
                ),
                1,
            ),
        ],
    ),
]

# 4. Métriques du benchmark
def ndcg_at_k(
    relevances: list[int],
    k: int,
) -> float:
    def dcg(values):
        return sum(
            ((2 ** rel) - 1)
            / np.log2(index + 2)
            for index, rel in enumerate(values[:k])
        )

    actual = dcg(relevances)

    ideal = dcg(
        sorted(
            relevances,
            reverse=True,
        )
    )

    if ideal == 0:
        return 0.0

    return actual / ideal

# 5. Exécution du benchmark
def main() -> None:
    scorer = SemanticJobRelevanceScorer()

    ndcgs = []

    for case in BENCHMARK:
        results = []

        for item in case.items:
            score = scorer.score(
                query=case.query,
                job=item.job,
            )

            results.append(
                (
                    item,
                    score,
                )
            )

        results.sort(
            key=lambda item: item[1].score,
            reverse=True,
        )

        ranked_relevances = [
            item.relevance
            for item, _ in results
        ]

        ndcg = ndcg_at_k(
            ranked_relevances,
            k=len(results),
        )

        ndcgs.append(ndcg)

        print()
        print("=" * 100)
        print(f"QUERY: {case.query}")
        print("=" * 100)

        for position, (
            item,
            score,
        ) in enumerate(
            results,
            start=1,
        ):
            print(
                f"{position}. "
                f"[rel={item.relevance}] "
                f"score={score.score:.4f} "
                f"title={score.title:.4f} "
                f"skills={score.skills:.4f} "
                f"description={score.description:.4f} "
                f"| {item.job.title}"
            )

        print(
            f"\nNDCG: {ndcg:.3f}"
        )

    print()
    print(
        f"MEAN NDCG: {np.mean(ndcgs):.3f}"
    )

# 6. Point d'entrée
if __name__ == "__main__":
    main()
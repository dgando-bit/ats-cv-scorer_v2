from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class Candidate:
    text: str
    relevant: bool


@dataclass
class BenchmarkCase:
    query: str
    candidates: list[Candidate]


BENCHMARK = [
    BenchmarkCase(
        query="machine learning",
        candidates=[
            Candidate(
                "Data Scientist spécialisé dans la conception, "
                "l'entraînement et le déploiement de modèles "
                "prédictifs.",
                True,
            ),
            Candidate(
                "Machine Learning Engineer chargé "
                "d'industrialiser des modèles d'intelligence "
                "artificielle.",
                True,
            ),
            Candidate(
                "Data Analyst chargé du reporting Power BI "
                "et de l'analyse décisionnelle.",
                False,
            ),
            Candidate(
                "Ingénieur cybersécurité spécialisé dans les "
                "tests d'intrusion, SOC et gestion des risques.",
                False,
            ),
            Candidate(
                "Comptable fournisseurs chargé de la saisie "
                "et du rapprochement des factures.",
                False,
            ),
        ],
    ),
    BenchmarkCase(
        query="comptable",
        candidates=[
            Candidate(
                "Comptable fournisseurs chargé du traitement "
                "des factures et des rapprochements bancaires.",
                True,
            ),
            Candidate(
                "Comptable général responsable des clôtures "
                "mensuelles et des écritures comptables.",
                True,
            ),
            Candidate(
                "Contrôleur de gestion chargé des budgets "
                "et du suivi des indicateurs financiers.",
                False,
            ),
            Candidate(
                "Business Developer chargé de la prospection "
                "et de la négociation commerciale.",
                False,
            ),
            Candidate(
                "Développeur backend Python spécialisé "
                "dans les APIs REST.",
                False,
            ),
        ],
    ),
    BenchmarkCase(
        query="infirmier",
        candidates=[
            Candidate(
                "Infirmier en bloc opératoire assurant "
                "la prise en charge des patients et "
                "l'assistance chirurgicale.",
                True,
            ),
            Candidate(
                "Infirmier diplômé d'État chargé des soins, "
                "du suivi clinique et de l'accompagnement "
                "des patients.",
                True,
            ),
            Candidate(
                "Aide-soignant chargé de l'accompagnement "
                "quotidien des patients.",
                False,
            ),
            Candidate(
                "Technicien de maintenance industrielle.",
                False,
            ),
            Candidate(
                "Développeur frontend React et TypeScript.",
                False,
            ),
        ],
    ),
    BenchmarkCase(
        query="commercial",
        candidates=[
            Candidate(
                "Commercial terrain chargé de développer "
                "un portefeuille clients et de négocier "
                "des contrats.",
                True,
            ),
            Candidate(
                "Business Developer responsable de la "
                "prospection, du développement commercial "
                "et de la négociation.",
                True,
            ),
            Candidate(
                "Responsable marketing chargé des campagnes "
                "d'acquisition et de communication.",
                False,
            ),
            Candidate(
                "Comptable fournisseurs chargé des factures.",
                False,
            ),
            Candidate(
                "Administrateur systèmes et réseaux.",
                False,
            ),
        ],
    ),
    BenchmarkCase(
        query="chef de projet",
        candidates=[
            Candidate(
                "Chef de projet chargé de coordonner les "
                "équipes, le planning, le budget et les "
                "livrables.",
                True,
            ),
            Candidate(
                "Project Manager responsable du pilotage "
                "des projets, des délais et des parties "
                "prenantes.",
                True,
            ),
            Candidate(
                "Product Owner chargé du backlog produit "
                "et de la priorisation des fonctionnalités.",
                False,
            ),
            Candidate(
                "Technicien de maintenance industrielle.",
                False,
            ),
            Candidate(
                "Comptable général chargé des clôtures.",
                False,
            ),
        ],
    ),
]


MODELS = [
    "intfloat/multilingual-e5-small",
    "BAAI/bge-m3",
]


def encode(
    model: SentenceTransformer,
    model_name: str,
    query: str,
    documents: list[str],
) -> tuple[np.ndarray, np.ndarray]:

    if "e5" in model_name.lower():
        query_text = f"query: {query}"

        document_texts = [
            f"passage: {document}"
            for document in documents
        ]
    else:
        query_text = query
        document_texts = documents

    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True,
    )[0]

    document_embeddings = model.encode(
        document_texts,
        normalize_embeddings=True,
    )

    return query_embedding, document_embeddings


def reciprocal_rank(
    ranked_relevance: list[bool],
) -> float:
    for rank, relevant in enumerate(
        ranked_relevance,
        start=1,
    ):
        if relevant:
            return 1.0 / rank

    return 0.0


def recall_at_k(
    ranked_relevance: list[bool],
    total_relevant: int,
    k: int,
) -> float:
    if total_relevant == 0:
        return 0.0

    found = sum(
        ranked_relevance[:k]
    )

    return found / total_relevant


def evaluate_model(
    model_name: str,
) -> None:
    print("\n")
    print("=" * 90)
    print(f"MODEL: {model_name}")
    print("=" * 90)

    model = SentenceTransformer(
        model_name
    )

    reciprocal_ranks = []
    recalls_at_2 = []

    for case in BENCHMARK:
        documents = [
            candidate.text
            for candidate in case.candidates
        ]

        query_embedding, document_embeddings = (
            encode(
                model=model,
                model_name=model_name,
                query=case.query,
                documents=documents,
            )
        )

        scores = (
            document_embeddings
            @ query_embedding
        )

        ranking = np.argsort(scores)[::-1]

        ranked_relevance = [
            case.candidates[index].relevant
            for index in ranking
        ]

        total_relevant = sum(
            candidate.relevant
            for candidate in case.candidates
        )

        rr = reciprocal_rank(
            ranked_relevance
        )

        recall_2 = recall_at_k(
            ranked_relevance,
            total_relevant,
            k=2,
        )

        reciprocal_ranks.append(rr)
        recalls_at_2.append(recall_2)

        print(
            f"\nQUERY: {case.query}"
        )
        print("-" * 90)

        for position, index in enumerate(
            ranking,
            start=1,
        ):
            candidate = case.candidates[index]

            marker = (
                "✓"
                if candidate.relevant
                else "✗"
            )

            print(
                f"{position}. "
                f"[{marker}] "
                f"{scores[index]:.4f} "
                f"{candidate.text}"
            )

        print(
            f"\nMRR query: {rr:.3f}"
        )
        print(
            f"Recall@2: {recall_2:.3f}"
        )

    mean_rr = float(
        np.mean(reciprocal_ranks)
    )

    mean_recall_2 = float(
        np.mean(recalls_at_2)
    )

    print("\n" + "-" * 90)

    print(
        f"MEAN MRR:      {mean_rr:.3f}"
    )

    print(
        f"MEAN Recall@2: {mean_recall_2:.3f}"
    )


def main():
    for model_name in MODELS:
        evaluate_model(model_name)


if __name__ == "__main__":
    main()
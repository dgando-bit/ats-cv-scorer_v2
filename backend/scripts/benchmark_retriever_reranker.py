from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer

from app.services.semantic.job_reranker import (
    JobReranker,
)


@dataclass
class Candidate:
    text: str
    relevance: int


@dataclass
class BenchmarkCase:
    query: str
    candidates: list[Candidate]


BENCHMARK = [
    BenchmarkCase(
        query="machine learning",
        candidates=[
            Candidate(
                "Data Scientist spécialisé dans la "
                "modélisation prédictive, l'entraînement "
                "de modèles et leur mise en production.",
                3,
            ),
            Candidate(
                "AI Engineer responsable de la conception "
                "et de l'industrialisation de modèles "
                "d'intelligence artificielle.",
                3,
            ),
            Candidate(
                "Data Analyst spécialisé dans SQL, "
                "Power BI, reporting et analyse "
                "décisionnelle.",
                1,
            ),
            Candidate(
                "Ingénieur cybersécurité spécialisé dans "
                "la détection des menaces et les tests "
                "d'intrusion.",
                0,
            ),
            Candidate(
                "Software Engineer chargé du développement "
                "d'APIs et de services backend.",
                0,
            ),
        ],
    ),
    BenchmarkCase(
        query="commercial B2B",
        candidates=[
            Candidate(
                "Account Executive SaaS responsable du "
                "cycle de vente, de la prospection et de "
                "la négociation avec des entreprises.",
                3,
            ),
            Candidate(
                "Business Developer grands comptes chargé "
                "de développer un portefeuille de clients "
                "professionnels.",
                3,
            ),
            Candidate(
                "Customer Success Manager chargé de "
                "fidéliser et accompagner un portefeuille "
                "de clients professionnels.",
                1,
            ),
            Candidate(
                "Responsable marketing acquisition chargé "
                "des campagnes digitales et de la "
                "génération de leads.",
                1,
            ),
            Candidate(
                "Acheteur industriel responsable des "
                "relations fournisseurs et des "
                "négociations d'achats.",
                0,
            ),
        ],
    ),
    BenchmarkCase(
        query="infirmier",
        candidates=[
            Candidate(
                "IDE en service de réanimation chargé "
                "des soins aux patients et de leur "
                "surveillance clinique.",
                3,
            ),
            Candidate(
                "IDE bloc opératoire participant à la "
                "prise en charge périopératoire des "
                "patients.",
                3,
            ),
            Candidate(
                "Aide-soignant assurant les soins "
                "d'hygiène et l'accompagnement quotidien "
                "des patients.",
                1,
            ),
            Candidate(
                "Médecin généraliste assurant le "
                "diagnostic et le suivi médical des "
                "patients.",
                1,
            ),
            Candidate(
                "Secrétaire médicale chargée de l'accueil "
                "et de la gestion administrative.",
                0,
            ),
        ],
    ),
    BenchmarkCase(
        query="gestion de paie",
        candidates=[
            Candidate(
                "Payroll Specialist responsable de "
                "l'établissement des bulletins, des "
                "déclarations sociales et du suivi des "
                "salariés.",
                3,
            ),
            Candidate(
                "Gestionnaire administration du personnel "
                "chargé des bulletins de salaire, des "
                "cotisations sociales et des absences.",
                3,
            ),
            Candidate(
                "Responsable RH chargé du recrutement, "
                "des relations sociales et de la politique "
                "de ressources humaines.",
                1,
            ),
            Candidate(
                "Comptable chargé des écritures, des "
                "factures et des clôtures comptables.",
                1,
            ),
            Candidate(
                "Contrôleur de gestion chargé du budget "
                "et des indicateurs financiers.",
                0,
            ),
        ],
    ),
    BenchmarkCase(
        query="chef de projet",
        candidates=[
            Candidate(
                "Project Manager responsable du planning, "
                "du budget, des risques, des équipes et "
                "des livrables.",
                3,
            ),
            Candidate(
                "Responsable de programme chargé de "
                "coordonner plusieurs projets, les "
                "ressources et les parties prenantes.",
                2,
            ),
            Candidate(
                "Product Owner chargé de prioriser le "
                "backlog et de définir les fonctionnalités "
                "du produit.",
                1,
            ),
            Candidate(
                "Scrum Master accompagnant les équipes "
                "agiles et facilitant les cérémonies.",
                1,
            ),
            Candidate(
                "Technicien maintenance chargé du "
                "diagnostic et de la réparation "
                "d'équipements industriels.",
                0,
            ),
        ],
    ),
    BenchmarkCase(
        query="développeur backend",
        candidates=[
            Candidate(
                "Software Engineer spécialisé dans la "
                "conception d'APIs REST, les bases de "
                "données et les services côté serveur.",
                3,
            ),
            Candidate(
                "Ingénieur logiciel travaillant sur des "
                "microservices, PostgreSQL et des systèmes "
                "distribués.",
                3,
            ),
            Candidate(
                "DevOps Engineer chargé des pipelines "
                "CI/CD, Kubernetes et de "
                "l'infrastructure cloud.",
                1,
            ),
            Candidate(
                "Frontend Engineer spécialisé dans React, "
                "CSS et interfaces utilisateur.",
                1,
            ),
            Candidate(
                "Administrateur réseau chargé des "
                "équipements et de la connectivité.",
                0,
            ),
        ],
    ),
]


def dcg_at_k(
    relevances: list[int],
    k: int,
) -> float:
    score = 0.0

    for index, relevance in enumerate(
        relevances[:k]
    ):
        gain = (2 ** relevance) - 1
        discount = np.log2(index + 2)

        score += gain / discount

    return float(score)


def ndcg_at_k(
    ranked_relevances: list[int],
    k: int,
) -> float:
    actual = dcg_at_k(
        ranked_relevances,
        k,
    )

    ideal = dcg_at_k(
        sorted(
            ranked_relevances,
            reverse=True,
        ),
        k,
    )

    if ideal == 0:
        return 0.0

    return actual / ideal


def reciprocal_rank(
    ranked_relevances: list[int],
) -> float:
    for rank, relevance in enumerate(
        ranked_relevances,
        start=1,
    ):
        if relevance >= 2:
            return 1.0 / rank

    return 0.0


def recall_at_2(
    ranked_relevances: list[int],
) -> float:
    relevant_positions = [
        relevance
        for relevance in ranked_relevances
        if relevance >= 2
    ]

    total_relevant = len(
        relevant_positions
    )

    if total_relevant == 0:
        return 0.0

    found = sum(
        relevance >= 2
        for relevance in ranked_relevances[:2]
    )

    return (
        found
        / min(total_relevant, 2)
    )


def main() -> None:
    retriever = SentenceTransformer(
        "intfloat/multilingual-e5-small"
    )

    reranker = JobReranker()

    retriever_metrics = []
    reranker_metrics = []

    for case in BENCHMARK:
        documents = [
            candidate.text
            for candidate in case.candidates
        ]

        query_embedding = retriever.encode(
            [f"query: {case.query}"],
            normalize_embeddings=True,
        )[0]

        document_embeddings = retriever.encode(
            [
                f"passage: {document}"
                for document in documents
            ],
            normalize_embeddings=True,
        )

        retriever_scores = (
            document_embeddings
            @ query_embedding
        )

        retriever_ranking = (
            np.argsort(
                retriever_scores
            )[::-1]
        )

        retriever_relevance = [
            case.candidates[index].relevance
            for index in retriever_ranking
        ]

        reranked = reranker.rank(
            query=case.query,
            documents=documents,
        )

        reranker_ranking = [
            index
            for index, _ in reranked
        ]

        reranker_relevance = [
            case.candidates[index].relevance
            for index in reranker_ranking
        ]

        retriever_result = (
            reciprocal_rank(
                retriever_relevance
            ),
            recall_at_2(
                retriever_relevance
            ),
            ndcg_at_k(
                retriever_relevance,
                5,
            ),
        )

        reranker_result = (
            reciprocal_rank(
                reranker_relevance
            ),
            recall_at_2(
                reranker_relevance
            ),
            ndcg_at_k(
                reranker_relevance,
                5,
            ),
        )

        retriever_metrics.append(
            retriever_result
        )

        reranker_metrics.append(
            reranker_result
        )

        print("\n")
        print("=" * 100)
        print(
            f"QUERY: {case.query}"
        )
        print("=" * 100)

        print("\nE5 RETRIEVER")
        print("-" * 100)

        for position, index in enumerate(
            retriever_ranking,
            start=1,
        ):
            candidate = case.candidates[
                index
            ]

            print(
                f"{position}. "
                f"[rel={candidate.relevance}] "
                f"{retriever_scores[index]:.4f} "
                f"{candidate.text}"
            )

        print("\nCROSSENCODER RERANKER")
        print("-" * 100)

        for position, (
            index,
            score,
        ) in enumerate(
            reranked,
            start=1,
        ):
            candidate = case.candidates[
                index
            ]

            print(
                f"{position}. "
                f"[rel={candidate.relevance}] "
                f"{score:.4f} "
                f"{candidate.text}"
            )

        print("\nMETRICS")

        print(
            "E5     "
            f"MRR={retriever_result[0]:.3f} "
            f"Recall@2={retriever_result[1]:.3f} "
            f"NDCG@5={retriever_result[2]:.3f}"
        )

        print(
            "RERANK  "
            f"MRR={reranker_result[0]:.3f} "
            f"Recall@2={reranker_result[1]:.3f} "
            f"NDCG@5={reranker_result[2]:.3f}"
        )

    retriever_array = np.array(
        retriever_metrics
    )

    reranker_array = np.array(
        reranker_metrics
    )

    print("\n\n")
    print("=" * 100)
    print("FINAL RESULTS")
    print("=" * 100)

    print(
        "\nE5-small"
    )

    print(
        f"MRR:      "
        f"{retriever_array[:, 0].mean():.3f}"
    )

    print(
        f"Recall@2: "
        f"{retriever_array[:, 1].mean():.3f}"
    )

    print(
        f"NDCG@5:   "
        f"{retriever_array[:, 2].mean():.3f}"
    )

    print(
        "\nE5-small + CrossEncoder"
    )

    print(
        f"MRR:      "
        f"{reranker_array[:, 0].mean():.3f}"
    )

    print(
        f"Recall@2: "
        f"{reranker_array[:, 1].mean():.3f}"
    )

    print(
        f"NDCG@5:   "
        f"{reranker_array[:, 2].mean():.3f}"
    )


if __name__ == "__main__":
    main()
from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class Candidate:
    text: str

    # 3 = très pertinent
    # 2 = pertinent
    # 1 = métier / domaine proche
    # 0 = non pertinent
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
    BenchmarkCase(
        query="comptabilité fournisseurs",
        candidates=[
            Candidate(
                "Accounts Payable Specialist chargé du "
                "traitement des factures fournisseurs, "
                "des paiements et des rapprochements.",
                3,
            ),
            Candidate(
                "Chargé de comptabilité responsable de "
                "la saisie des factures d'achat et du "
                "suivi des fournisseurs.",
                3,
            ),
            Candidate(
                "Comptable général chargé des clôtures, "
                "provisions et écritures comptables.",
                2,
            ),
            Candidate(
                "Contrôleur financier chargé du reporting "
                "et du suivi budgétaire.",
                1,
            ),
            Candidate(
                "Commercial grands comptes responsable "
                "du développement des ventes.",
                0,
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

    return (
        query_embedding,
        document_embeddings,
    )


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
    actual_dcg = dcg_at_k(
        ranked_relevances,
        k,
    )

    ideal_relevances = sorted(
        ranked_relevances,
        reverse=True,
    )

    ideal_dcg = dcg_at_k(
        ideal_relevances,
        k,
    )

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


def reciprocal_rank(
    ranked_relevances: list[int],
) -> float:
    """
    Pour le MRR, relevance >= 2 est considérée
    comme réellement pertinente.
    """

    for rank, relevance in enumerate(
        ranked_relevances,
        start=1,
    ):
        if relevance >= 2:
            return 1.0 / rank

    return 0.0


def recall_at_k(
    ranked_relevances: list[int],
    total_relevant: int,
    k: int,
) -> float:
    if total_relevant == 0:
        return 0.0

    found = sum(
        relevance >= 2
        for relevance in ranked_relevances[:k]
    )

    return found / total_relevant


def evaluate_model(
    model_name: str,
) -> None:
    print("\n")
    print("=" * 100)
    print(f"MODEL: {model_name}")
    print("=" * 100)

    model = SentenceTransformer(
        model_name
    )

    reciprocal_ranks = []
    recalls_at_2 = []
    ndcgs_at_5 = []

    for case in BENCHMARK:
        documents = [
            candidate.text
            for candidate in case.candidates
        ]

        (
            query_embedding,
            document_embeddings,
        ) = encode(
            model=model,
            model_name=model_name,
            query=case.query,
            documents=documents,
        )

        scores = (
            document_embeddings
            @ query_embedding
        )

        ranking = np.argsort(scores)[::-1]

        ranked_relevances = [
            case.candidates[index].relevance
            for index in ranking
        ]

        total_relevant = sum(
            candidate.relevance >= 2
            for candidate in case.candidates
        )

        rr = reciprocal_rank(
            ranked_relevances
        )

        recall_2 = recall_at_k(
            ranked_relevances,
            total_relevant,
            k=2,
        )

        ndcg_5 = ndcg_at_k(
            ranked_relevances,
            k=5,
        )

        reciprocal_ranks.append(rr)
        recalls_at_2.append(recall_2)
        ndcgs_at_5.append(ndcg_5)

        print(f"\nQUERY: {case.query}")
        print("-" * 100)

        for position, index in enumerate(
            ranking,
            start=1,
        ):
            candidate = case.candidates[index]

            print(
                f"{position}. "
                f"[rel={candidate.relevance}] "
                f"{scores[index]:.4f} "
                f"{candidate.text}"
            )

        print(
            f"\nMRR:      {rr:.3f}"
        )
        print(
            f"Recall@2: {recall_2:.3f}"
        )
        print(
            f"NDCG@5:   {ndcg_5:.3f}"
        )

    print("\n" + "-" * 100)

    print(
        f"MEAN MRR:      "
        f"{np.mean(reciprocal_ranks):.3f}"
    )

    print(
        f"MEAN Recall@2: "
        f"{np.mean(recalls_at_2):.3f}"
    )

    print(
        f"MEAN NDCG@5:   "
        f"{np.mean(ndcgs_at_5):.3f}"
    )


def main() -> None:
    for model_name in MODELS:
        evaluate_model(model_name)


if __name__ == "__main__":
    main()
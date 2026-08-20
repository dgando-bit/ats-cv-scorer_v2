from dataclasses import dataclass

import numpy as np

from app.models.job import JobOffer
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)


@dataclass
class BenchmarkItem:
    job: JobOffer
    relevance: int


@dataclass
class BenchmarkCase:
    query: str
    items: list[BenchmarkItem]


BENCHMARK = [
    BenchmarkCase(
        query="machine learning",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Data Scientist",
                    description=(
                        "Modélisation prédictive, entraînement "
                        "de modèles et mise en production."
                    ),
                    skills=[
                        "Python",
                        "Machine Learning",
                        "Scikit-learn",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="AI Engineer",
                    description=(
                        "Conception et industrialisation "
                        "de modèles d'intelligence artificielle."
                    ),
                    skills=[
                        "Python",
                        "Deep Learning",
                        "MLOps",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Data Analyst",
                    description=(
                        "Reporting, analyse décisionnelle "
                        "et création de tableaux de bord."
                    ),
                    skills=[
                        "SQL",
                        "Power BI",
                        "Excel",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Ingénieur cybersécurité",
                    description=(
                        "Détection des menaces et tests "
                        "d'intrusion."
                    ),
                    skills=[
                        "SOC",
                        "SIEM",
                        "Pentest",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="commercial B2B",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Account Executive SaaS",
                    description=(
                        "Prospection, cycle de vente et "
                        "négociation avec des entreprises."
                    ),
                    skills=[
                        "Prospection",
                        "Vente B2B",
                        "Négociation",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Business Developer grands comptes",
                    description=(
                        "Développement d'un portefeuille "
                        "de clients professionnels."
                    ),
                    skills=[
                        "Business Development",
                        "Prospection",
                        "Vente",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Customer Success Manager",
                    description=(
                        "Accompagnement et fidélisation "
                        "des clients professionnels."
                    ),
                    skills=[
                        "Relation client",
                        "SaaS",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Responsable marketing acquisition",
                    description=(
                        "Campagnes digitales et génération "
                        "de leads."
                    ),
                    skills=[
                        "Marketing",
                        "SEO",
                        "SEA",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Acheteur industriel",
                    description=(
                        "Gestion des fournisseurs et "
                        "négociation des achats."
                    ),
                    skills=[
                        "Achats",
                        "Négociation fournisseurs",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="infirmier",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="IDE réanimation",
                    description=(
                        "Soins aux patients et surveillance "
                        "clinique en réanimation."
                    ),
                    skills=[
                        "Soins infirmiers",
                        "Réanimation",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="IDE bloc opératoire",
                    description=(
                        "Prise en charge périopératoire "
                        "des patients."
                    ),
                    skills=[
                        "Soins infirmiers",
                        "Bloc opératoire",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Aide-soignant",
                    description=(
                        "Soins d'hygiène et accompagnement "
                        "quotidien des patients."
                    ),
                    skills=[
                        "Soins",
                        "Accompagnement",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Médecin généraliste",
                    description=(
                        "Diagnostic et suivi médical "
                        "des patients."
                    ),
                    skills=[
                        "Médecine",
                        "Diagnostic",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Secrétaire médicale",
                    description=(
                        "Accueil des patients et gestion "
                        "administrative."
                    ),
                    skills=[
                        "Accueil",
                        "Administration",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="gestion de paie",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Payroll Specialist",
                    description=(
                        "Établissement des bulletins et "
                        "déclarations sociales."
                    ),
                    skills=[
                        "Paie",
                        "DSN",
                        "Cotisations sociales",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Gestionnaire administration du personnel",
                    description=(
                        "Gestion des bulletins de salaire, "
                        "cotisations et absences."
                    ),
                    skills=[
                        "Paie",
                        "Administration du personnel",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Responsable RH",
                    description=(
                        "Recrutement, relations sociales "
                        "et politique RH."
                    ),
                    skills=[
                        "RH",
                        "Recrutement",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Comptable",
                    description=(
                        "Écritures, factures et clôtures "
                        "comptables."
                    ),
                    skills=[
                        "Comptabilité",
                        "Facturation",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Contrôleur de gestion",
                    description=(
                        "Suivi budgétaire et analyse "
                        "des indicateurs financiers."
                    ),
                    skills=[
                        "Budget",
                        "Reporting",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="chef de projet",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Project Manager",
                    description=(
                        "Pilotage du planning, du budget, "
                        "des risques et des livrables."
                    ),
                    skills=[
                        "Gestion de projet",
                        "Planning",
                        "Budget",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Responsable de programme",
                    description=(
                        "Coordination de plusieurs projets, "
                        "ressources et parties prenantes."
                    ),
                    skills=[
                        "Programme",
                        "Gestion de projet",
                    ],
                ),
                relevance=2,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Product Owner",
                    description=(
                        "Priorisation du backlog et définition "
                        "des fonctionnalités produit."
                    ),
                    skills=[
                        "Agile",
                        "Backlog",
                        "Product Management",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Scrum Master",
                    description=(
                        "Accompagnement des équipes agiles "
                        "et animation des cérémonies."
                    ),
                    skills=[
                        "Scrum",
                        "Agile",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Technicien maintenance",
                    description=(
                        "Diagnostic et réparation "
                        "d'équipements industriels."
                    ),
                    skills=[
                        "Maintenance",
                        "Diagnostic",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="développeur backend",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Software Engineer",
                    description=(
                        "Conception d'APIs REST, microservices "
                        "et services côté serveur."
                    ),
                    skills=[
                        "Python",
                        "FastAPI",
                        "PostgreSQL",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Ingénieur logiciel",
                    description=(
                        "Développement de microservices, "
                        "APIs et systèmes distribués."
                    ),
                    skills=[
                        "Python",
                        "PostgreSQL",
                        "Docker",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
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
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Frontend Engineer",
                    description=(
                        "Développement d'interfaces web "
                        "avec React."
                    ),
                    skills=[
                        "React",
                        "TypeScript",
                        "CSS",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Administrateur réseau",
                    description=(
                        "Administration des équipements "
                        "et de la connectivité réseau."
                    ),
                    skills=[
                        "TCP/IP",
                        "Cisco",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
    BenchmarkCase(
        query="comptabilité fournisseurs",
        items=[
            BenchmarkItem(
                job=JobOffer(
                    title="Accounts Payable Specialist",
                    description=(
                        "Traitement des factures fournisseurs, "
                        "paiements et rapprochements."
                    ),
                    skills=[
                        "Accounts Payable",
                        "Facturation",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Chargé de comptabilité fournisseurs",
                    description=(
                        "Saisie des factures d'achat et "
                        "suivi des fournisseurs."
                    ),
                    skills=[
                        "Comptabilité fournisseurs",
                        "Factures",
                    ],
                ),
                relevance=3,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Comptable général",
                    description=(
                        "Clôtures, provisions et écritures "
                        "comptables."
                    ),
                    skills=[
                        "Comptabilité",
                        "Clôture",
                    ],
                ),
                relevance=2,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Contrôleur financier",
                    description=(
                        "Reporting financier et suivi "
                        "budgétaire."
                    ),
                    skills=[
                        "Finance",
                        "Reporting",
                    ],
                ),
                relevance=1,
            ),
            BenchmarkItem(
                job=JobOffer(
                    title="Commercial grands comptes",
                    description=(
                        "Développement des ventes auprès "
                        "des clients stratégiques."
                    ),
                    skills=[
                        "Vente",
                        "Négociation",
                    ],
                ),
                relevance=0,
            ),
        ],
    ),
]


def dcg_at_k(
    relevances: list[int],
    k: int,
) -> float:
    return sum(
        ((2 ** relevance) - 1)
        / np.log2(index + 2)
        for index, relevance in enumerate(
            relevances[:k]
        )
    )


def ndcg_at_k(
    relevances: list[int],
    k: int,
) -> float:
    actual = dcg_at_k(
        relevances,
        k,
    )

    ideal = dcg_at_k(
        sorted(
            relevances,
            reverse=True,
        ),
        k,
    )

    if ideal == 0:
        return 0.0

    return actual / ideal


def reciprocal_rank(
    relevances: list[int],
) -> float:
    for rank, relevance in enumerate(
        relevances,
        start=1,
    ):
        if relevance >= 2:
            return 1.0 / rank

    return 0.0


def recall_at_2(
    relevances: list[int],
) -> float:
    total_relevant = sum(
        relevance >= 2
        for relevance in relevances
    )

    if total_relevant == 0:
        return 0.0

    found = sum(
        relevance >= 2
        for relevance in relevances[:2]
    )

    # Au maximum 2 résultats peuvent être
    # récupérés dans un Recall@2.
    return found / min(
        total_relevant,
        2,
    )


def main() -> None:
    evaluator = (
        GroqJobRelevanceEvaluator()
    )

    metrics = []

    for case in BENCHMARK:
        results = []

        for item in case.items:
            evaluation = evaluator.evaluate(
                query=case.query,
                job=item.job,
            )

            results.append(
                (
                    item,
                    evaluation,
                )
            )

        results.sort(
            key=lambda item: (
                item[1].relevance
            ),
            reverse=True,
        )

        relevances = [
            item.relevance
            for item, _ in results
        ]

        mrr = reciprocal_rank(
            relevances
        )

        recall = recall_at_2(
            relevances
        )

        ndcg = ndcg_at_k(
            relevances,
            k=min(
                5,
                len(relevances),
            ),
        )

        metrics.append(
            (
                mrr,
                recall,
                ndcg,
            )
        )

        print()
        print("=" * 100)
        print(
            f"QUERY: {case.query}"
        )
        print("=" * 100)

        for position, (
            item,
            evaluation,
        ) in enumerate(
            results,
            start=1,
        ):
            print()
            print(
                f"{position}. "
                f"[rel={item.relevance}] "
                f"{evaluation.relevance:.3f} "
                f"| {item.job.title}"
            )

            print(
                f"   {evaluation.reason}"
            )

        print()
        print(
            f"MRR:      {mrr:.3f}"
        )
        print(
            f"Recall@2: {recall:.3f}"
        )
        print(
            f"NDCG@5:   {ndcg:.3f}"
        )

    values = np.array(
        metrics
    )

    print("\n")
    print("=" * 100)
    print("FINAL RESULTS")
    print("=" * 100)

    print(
        f"MEAN MRR:      "
        f"{values[:, 0].mean():.3f}"
    )

    print(
        f"MEAN Recall@2: "
        f"{values[:, 1].mean():.3f}"
    )

    print(
        f"MEAN NDCG@5:   "
        f"{values[:, 2].mean():.3f}"
    )


if __name__ == "__main__":
    main()
from app.services.semantic.semantic_similarity_service import (
    SemanticSimilarityService,
)


def main():
    service = SemanticSimilarityService()

    pairs = [
        (
            "machine learning",
            "Data Scientist spécialisé dans la conception "
            "et le déploiement de modèles prédictifs.",
        ),
        (
            "machine learning",
            "Data Analyst chargé du reporting Power BI "
            "et de l'analyse décisionnelle.",
        ),
        (
            "machine learning",
            "Ingénieur cybersécurité spécialisé dans les "
            "tests d'intrusion, SOC et gestion des risques.",
        ),
        (
            "comptable",
            "Comptable fournisseurs chargé de la saisie "
            "des factures et des rapprochements bancaires.",
        ),
        (
            "infirmier",
            "Infirmier en bloc opératoire assurant la prise "
            "en charge des patients et l'assistance chirurgicale.",
        ),
        (
            "commercial",
            "Business Developer responsable de la prospection, "
            "du développement de portefeuille et de la négociation.",
        ),
    ]

    print("\n=== SEMANTIC SIMILARITY ===\n")

    for query, document in pairs:
        score = service.similarity(
            query=query,
            document=document,
        )

        print(f"QUERY: {query}")
        print(f"DOCUMENT: {document}")
        print(f"SCORE: {score:.4f}")
        print("-" * 80)


if __name__ == "__main__":
    main()
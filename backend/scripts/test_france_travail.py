from app.providers.france_travail import FranceTravailProvider


def main():
    provider = FranceTravailProvider()

    jobs = provider.search_jobs(
        keywords="machine learning engineer",
        location="75101",
        limit=10,
    )

    print(f"\n{len(jobs)} offre(s) trouvée(s)\n")

    for job in jobs:
        print("=" * 80)
        print(f"ID       : {job.id}")
        print(f"Titre    : {job.title}")
        print(f"Entreprise: {job.company}")
        print(f"Lieu     : {job.location}")
        print(f"Contrat  : {job.contract_type}")
        print(f"Source   : {job.source}")
        print(f"URL      : {job.source_url}")

        description = job.description or ""

        print(
            f"Description: {description[:300]}..."
        )


if __name__ == "__main__":
    main()
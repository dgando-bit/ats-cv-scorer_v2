import json

from groq import Groq

from app.core.config import settings
from app.models.job import JobOffer
from app.models.job_relevance import (
    JobRelevanceEvaluation,
)
from app.models.job_relevance_batch import (
    BatchJobRelevanceResponse,
)
from app.services.llm.base import (
    JobRelevanceEvaluator,
)


class GroqJobRelevanceEvaluator(
    JobRelevanceEvaluator
):
    DEFAULT_MODEL = "openai/gpt-oss-20b"

    # On ne transmet pas toute l'annonce au reranker.
    #
    # E5 a déjà effectué le retrieval sémantique.
    # Ici Groq doit principalement distinguer les métiers
    # réellement pertinents.
    #
    # Cela réduit fortement la consommation TPM Groq.
    MAX_DESCRIPTION_CHARS = 900

    def __init__(
        self,
        client: Groq | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client or Groq(
            api_key=settings.groq_api_key
        )

        self.model = (
            model
            or settings.groq_model
            or self.DEFAULT_MODEL
        )

    # ============================================================
    # Évaluation d'une seule offre
    # ============================================================

    def evaluate(
        self,
        query: str,
        job: JobOffer,
    ) -> JobRelevanceEvaluation:

        if not query.strip():
            return JobRelevanceEvaluation(
                relevance=0.0,
                reason="Empty search query.",
            )

        skills = ", ".join(
            job.skills
        )

        user_content = f"""
SEARCH QUERY:
{query}

JOB TITLE:
{job.title}

JOB SKILLS:
{skills or "Not specified"}

JOB DESCRIPTION:
{job.description or "Not specified"}
""".strip()

        schema = (
            JobRelevanceEvaluation
            .model_json_schema()
        )

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You evaluate how relevant a "
                            "job offer is to a user's job "
                            "search. "
                            "Evaluate the occupation and "
                            "responsibilities, not the "
                            "candidate's suitability. "
                            "Be industry-agnostic. "
                            "Equivalent job titles, "
                            "synonyms, abbreviations and "
                            "titles in another language "
                            "can represent the same "
                            "occupation. "
                            "Carefully distinguish related "
                            "but different occupations. "
                            "Return relevance between "
                            "0 and 1."
                        ),
                    },
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": (
                            "job_relevance_evaluation"
                        ),
                        "strict": True,
                        "schema": schema,
                    },
                },
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        data = json.loads(
            content
        )

        return (
            JobRelevanceEvaluation
            .model_validate(
                data
            )
        )

    # ============================================================
    # Évaluation batch
    # ============================================================

    def evaluate_many(
        self,
        query: str,
        jobs: list[JobOffer],
    ) -> list[
        JobRelevanceEvaluation
    ]:

        if not jobs:
            return []

        if not query.strip():
            return [
                JobRelevanceEvaluation(
                    relevance=0.0,
                    reason=(
                        "Empty search query."
                    ),
                )
                for _ in jobs
            ]

        offers = []

        for index, job in enumerate(
            jobs
        ):
            description = (
                job.description
                or ""
            )

            description = (
                description[
                    :self.MAX_DESCRIPTION_CHARS
                ]
            )

            offers.append(
                {
                    "candidate_id": str(
                        index
                    ),
                    "title": (
                        job.title
                        or ""
                    ),
                    "description": (
                        description
                    ),
                }
            )

        user_content = json.dumps(
            {
                "search_query": query,
                "jobs": offers,
            },
            ensure_ascii=False,
        )

        schema = (
            BatchJobRelevanceResponse
            .model_json_schema()
        )

        response = (
            self.client
            .chat
            .completions
            .create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You rank job offers according "
                            "to their relevance to a job "
                            "search query. "

                            "Evaluate the occupation and "
                            "core responsibilities only. "
                            "Do NOT evaluate whether a "
                            "candidate is qualified. "

                            "Equivalent job titles, "
                            "synonyms, abbreviations and "
                            "translations may describe "
                            "the same occupation. "

                            "Carefully distinguish related "
                            "but different occupations. "

                            "For example, a Data Analyst "
                            "should not automatically "
                            "receive the same relevance as "
                            "a Machine Learning Engineer. "

                            "Return exactly one evaluation "
                            "for every candidate_id "
                            "provided. "

                            "Do not omit candidates. "
                            "Do not add candidates. "

                            "Each relevance score must be "
                            "between 0 and 1."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            user_content
                        ),
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": (
                            "batch_job_relevance"
                        ),
                        "strict": True,
                        "schema": schema,
                    },
                },
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        data = json.loads(
            content
        )

        batch_response = (
            BatchJobRelevanceResponse
            .model_validate(
                data
            )
        )

        # --------------------------------------------------------
        # Reconstituer l'ordre original
        # --------------------------------------------------------

        evaluation_by_id = {
            item.candidate_id: item
            for item
            in batch_response.evaluations
        }

        results: list[
            JobRelevanceEvaluation
        ] = []

        for index in range(
            len(jobs)
        ):
            candidate_id = str(
                index
            )

            item = (
                evaluation_by_id.get(
                    candidate_id
                )
            )

            # Le schéma/prompt demande exactement une réponse
            # par offre, mais on protège quand même le pipeline.
            if item is None:
                results.append(
                    JobRelevanceEvaluation(
                        relevance=0.0,
                        reason=(
                            "Missing batch "
                            "evaluation."
                        ),
                    )
                )

                continue

            results.append(
                JobRelevanceEvaluation(
                    relevance=(
                        item.relevance
                    ),
                    reason=(
                        item.reason
                    ),
                )
            )

        return results
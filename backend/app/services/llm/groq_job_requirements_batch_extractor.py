import json

from groq import Groq
from pydantic import BaseModel

from app.core.config import settings
from app.models.job import JobOffer
from app.models.job_requirements import (
    JobRequirements,
)
from app.services.jobs.job_requirements_normalizer import (
    JobRequirementsNormalizer,
)


class JobRequirementsBatch(BaseModel):
    requirements: list[JobRequirements]

def make_schema_strict(
        schema: dict,
) -> dict:
    """
    Recursively make a Pydantic JSON schema
    compatible with Groq strict structured outputs.
    """

    if not isinstance(schema, dict):
        return schema

    if schema.get("type") == "object":
        schema["additionalProperties"] = False

        properties = schema.get(
            "properties",
            {},
        )

        # En mode strict, toutes les propriétés
        # définies doivent être présentes dans required.
        schema["required"] = list(
            properties.keys()
        )

    for value in schema.values():
        if isinstance(value, dict):
            make_schema_strict(value)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    make_schema_strict(item)

    return schema

class GroqJobRequirementsBatchExtractor:
    # Même logique que GroqJobRelevanceEvaluator : on tronque
    # les descriptions pour limiter le nombre de tokens d'entrée
    # (coût, risque de rate limit) mais aussi, ici, pour laisser
    # assez de marge de tokens de sortie au modèle afin qu'il
    # puisse terminer le JSON structuré pour TOUTES les offres
    # du batch sans être coupé en cours de génération (c'est ce
    # qui provoquait les erreurs "Failed to validate JSON" /
    # failed_generation vide observées en pratique).
    MAX_DESCRIPTION_CHARS = 900

    # Sortie structurée pour plusieurs offres à la fois : prévoir
    # une marge confortable par offre plutôt que de dépendre du
    # maximum par défaut du modèle.
    MAX_COMPLETION_TOKENS_PER_JOB = 600
    MIN_COMPLETION_TOKENS = 2000

    def __init__(
        self,
        client: Groq | None = None,
        model: str | None = None,
    ) -> None:
        self.client = client or Groq(
            api_key=settings.groq_api_key,
            timeout=30.0,
            # Le pipeline retombe déjà sur le fallback
            # lexical (_apply_lexical_fallback) en cas
            # d'échec Groq. On ne veut pas que le SDK
            # retente en interne avant ça : ça ajoute une
            # latence invisible dans nos logs
            # [requirements-batch] sans bénéfice, puisque
            # le fallback applicatif est déjà rapide et fiable.
            max_retries=0,
        )

        self.model = (
            model
            or settings.groq_model
        )

    def extract(
        self,
        jobs: list[JobOffer],
    ) -> list[JobRequirements]:

        if not jobs:
            return []

        jobs_payload = [
            {
                "index": index,
                "title": job.title,
                "description": (
                    job.description or ""
                )[: self.MAX_DESCRIPTION_CHARS]
                or "Not specified",
            }
            for index, job in enumerate(
                jobs
            )
        ]

        user_content = json.dumps(
            jobs_payload,
            ensure_ascii=False,
        )

        schema = make_schema_strict(
            JobRequirementsBatch
            .model_json_schema()
        )

        max_completion_tokens = max(
            self.MIN_COMPLETION_TOKENS,
            len(jobs)
            * self.MAX_COMPLETION_TOKENS_PER_JOB,
        )

        response = (
            self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=(
                    max_completion_tokens
                ),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract structured job "
                            "requirements for every job "
                            "offer in the provided array. "
                            "Return one requirements object "
                            "per input job, in exactly the "
                            "same order. "

                            "Be industry-agnostic. "

                            "Only extract requirements "
                            "explicitly stated or clearly "
                            "implied by the offer. "
                            "Do not invent requirements. "

                            "Separate hard skills, tools, "
                            "soft skills, languages, "
                            "experience, education, "
                            "certifications and "
                            "responsibilities. "

                            "Professional activities and "
                            "domain knowledge can be hard "
                            "skills even when they are not "
                            "software technologies. "

                            "Examples of hard skills include "
                            "medical terminology, patient "
                            "administration, appointment "
                            "scheduling, billing, document "
                            "management, machine learning "
                            "or data analysis. "

                            "Examples of tools include "
                            "Python, Docker, Word, Excel, "
                            "Microsoft Office, WEDA, "
                            "Doctolib or other named "
                            "software. "

                            "Examples of soft skills include "
                            "organisation, communication, "
                            "rigour, autonomy, empathy, "
                            "stress management and "
                            "teamwork. "

                            "For experience ranges such as "
                            "'2 to 4 years', use min_years "
                            "2 and max_years 4. "

                            "For 'at least 3 years' or "
                            "'3 years minimum', use "
                            "min_years 3 and max_years null. "

                            "If an offer requires a diploma "
                            "or qualification, preserve the "
                            "meaningful education level or "
                            "qualification in "
                            "education_level. "

                            "Preserve meaningful "
                            "professional terminology."
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
                            "job_requirements_batch"
                        ),
                        "strict": True,
                        "schema": schema,
                    },
                },
            )
        )

        raw_content = (
            response
            .choices[0]
            .message
            .content
        )

        data = json.loads(
            raw_content
        )

        batch = (
            JobRequirementsBatch
            .model_validate(
                data
            )
        )

        if (
            len(batch.requirements)
            != len(jobs)
        ):
            raise ValueError(
                "Groq returned an unexpected "
                "number of job requirements."
            )

        return [
            JobRequirementsNormalizer.normalize(
                requirements
            )
            for requirements
            in batch.requirements
        ]

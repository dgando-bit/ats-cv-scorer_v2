import json

from groq import Groq

from app.core.config import settings
from app.models.job import JobOffer
from app.models.job_requirements import (
    JobRequirements,
)
from app.services.jobs.job_requirements_normalizer import (
    JobRequirementsNormalizer,
)

class GroqJobRequirementsExtractor:
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
        )

    def extract(
        self,
        job: JobOffer,
    ) -> JobRequirements:
        content = f"""
JOB TITLE:
{job.title}

JOB DESCRIPTION:
{job.description or "Not specified"}
""".strip()

        schema = JobRequirements.model_json_schema()

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract the requirements of a job offer "
                            "into the provided structured schema. "
                            "Be industry-agnostic. "
                            "Only extract requirements that are explicitly "
                            "stated or clearly implied by the offer. "
                            "Do not invent requirements. "
                            "Separate hard skills, tools, soft skills, "
                            "languages, experience, education, certifications "
                            "and responsibilities. "
                            "For an experience range such as '2 to 4 years', "
                            "set min_years to 2 and max_years to 4. "
                            "For 'at least 3 years', set min_years to 3 "
                            "and max_years to null. "
                            "Preserve meaningful professional terminology."
                        ),
                    },
                    {
                        "role": "user",
                        "content": content,
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "job_requirements",
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

        data = json.loads(raw_content)

        requirements = JobRequirements.model_validate(
            data
        )

        return JobRequirementsNormalizer.normalize(
            requirements
        )
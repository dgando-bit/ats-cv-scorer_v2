import json
import os

from groq import Groq

from app.models.job import JobOffer
from app.models.job_relevance import (
    JobRelevanceEvaluation,
)
from app.services.llm.base import (
    JobRelevanceEvaluator,
)
from app.core.config import settings

class GroqJobRelevanceEvaluator(
    JobRelevanceEvaluator
):
    DEFAULT_MODEL = "openai/gpt-oss-20b"

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

        skills = ", ".join(job.skills)

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
            self.client.chat.completions.create(
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

        data = json.loads(content)

        return (
            JobRelevanceEvaluation
            .model_validate(data)
        )
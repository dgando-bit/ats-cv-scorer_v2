import json

from groq import Groq

from app.core.config import settings
from app.models.job import JobOffer
from app.models.job_requirements import (
    ExperienceRequirement,
    JobRequirements,
)
from app.services.jobs.job_requirements_normalizer import (
    JobRequirementsNormalizer,
)


class GroqJobRequirementsExtractor:
    """
    Extract structured candidate requirements
    from a job offer using Groq.

    The extractor must distinguish:
    - candidate requirements;
    - job responsibilities;
    - company/background information.
    """

    # Une exigence candidat supérieure à cette valeur
    # est suffisamment inhabituelle pour être considérée
    # comme suspecte.
    #
    # Le but principal est d'empêcher des phrases telles que
    # "plus de 55 ans d'expérience dans l'industrie"
    # décrivant l'entreprise d'être interprétées comme
    # une exigence candidat.
    MAX_PLAUSIBLE_EXPERIENCE_YEARS = 25

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

        schema = (
            JobRequirements.model_json_schema()
        )

        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract only the candidate requirements "
                            "from the job offer into the provided "
                            "structured schema. "
                            "Be industry-agnostic. "
                            "Do not invent requirements. "

                            "IMPORTANT SCOPE RULE: "
                            "Distinguish candidate requirements from "
                            "company information, employer history, "
                            "marketing statements, project history, "
                            "customer statistics, company age, and "
                            "general background information. "
                            "Never interpret the company's years of "
                            "experience as years of experience required "
                            "from the candidate. "
                            "For example, a sentence such as "
                            "'the company has more than 55 years of "
                            "experience in complex industrial projects' "
                            "must NOT produce an experience requirement. "

                            "EXPERIENCE RULES: "
                            "Only extract years of experience when the "
                            "text clearly applies to the candidate or "
                            "candidate profile. "
                            "Typical signals include phrases such as "
                            "'you have', 'you possess', "
                            "'required experience', "
                            "'minimum experience', "
                            "'candidate must have', "
                            "'profil recherché', "
                            "'vous disposez de', "
                            "'vous avez', or equivalent wording. "
                            "For '2 to 4 years', set min_years=2 "
                            "and max_years=4. "
                            "For 'at least 3 years', set min_years=3 "
                            "and max_years=null. "
                            "When no candidate experience requirement "
                            "is stated, set both min_years and "
                            "max_years to null and context to null. "
                            "If the experience applies to a particular "
                            "role or domain, describe it concisely "
                            "in context. "

                            "HARD SKILLS RULES: "
                            "Return concise and atomic professional "
                            "capabilities. "
                            "Do not put ordinary job duties or verbose "
                            "responsibility sentences in hard_skills. "

                            "TOOLS RULES: "
                            "Return concrete programming languages, "
                            "software, frameworks, libraries, cloud "
                            "providers, platforms, databases, or other "
                            "specific technologies. "
                            "Do not return vague categories such as "
                            "'MLOps tools' or 'LLM frameworks'. "

                            "SOFT SKILLS RULES: "
                            "Return only behavioral or interpersonal "
                            "qualities requested from the candidate. "

                            "LANGUAGES RULES: "
                            "Extract candidate language requirements "
                            "and preserve the stated proficiency level "
                            "when available. "

                            "EDUCATION RULES: "
                            "Extract only education requirements for "
                            "the candidate. "

                            "CERTIFICATION RULES: "
                            "Extract only certifications expected or "
                            "required from the candidate. "

                            "RESPONSIBILITIES RULES: "
                            "Return the main duties of the position "
                            "as concise action-oriented phrases."
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

        data = json.loads(
            raw_content
        )

        requirements = (
            JobRequirements.model_validate(
                data
            )
        )

        requirements = (
            self._sanitize_experience(
                requirements
            )
        )

        return (
            JobRequirementsNormalizer
            .normalize(
                requirements
            )
        )

    @classmethod
    def _sanitize_experience(
        cls,
        requirements: JobRequirements,
    ) -> JobRequirements:
        """
        Protect the matching pipeline against obviously
        implausible experience requirements.

        Example:
        "55 years of experience" extracted from an employer's
        company history must not become a candidate requirement.

        This is deliberately only a safety net. The main
        semantic distinction must still be made by the LLM.
        """

        experience = requirements.experience

        values = [
            value
            for value in (
                experience.min_years,
                experience.max_years,
            )
            if value is not None
        ]

        if not values:
            return requirements

        if max(
            values
        ) <= cls.MAX_PLAUSIBLE_EXPERIENCE_YEARS:
            return requirements

        sanitized_experience = (
            ExperienceRequirement(
                min_years=None,
                max_years=None,
                context=None,
            )
        )

        return requirements.model_copy(
            update={
                "experience": (
                    sanitized_experience
                )
            }
        )
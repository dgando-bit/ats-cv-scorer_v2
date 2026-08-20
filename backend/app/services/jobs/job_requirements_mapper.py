from app.models.job import JobOffer
from app.models.job_requirements import (
    JobRequirements,
)


class JobRequirementsMapper:
    @staticmethod
    def to_job_offer(
        source_job: JobOffer,
        requirements: JobRequirements,
    ) -> JobOffer:
        languages = [
            requirement.language
            for requirement in requirements.languages
        ]

        experience_required = (
            JobRequirementsMapper._format_experience(
                requirements
            )
        )

        return JobOffer(
            id=source_job.id,
            title=source_job.title,
            company=source_job.company,
            location=source_job.location,
            contract_type=source_job.contract_type,
            description=source_job.description,
            skills=sorted(
                set(requirements.hard_skills)
            ),
            tools=sorted(
                set(requirements.tools)
            ),
            soft_skills=sorted(
                set(requirements.soft_skills)
            ),
            languages=languages,
            experience_required=experience_required,
            education_required=(
                requirements.education_level
            ),
            source=source_job.source,
            source_url=source_job.source_url,
        )

    @staticmethod
    def _format_experience(
        requirements: JobRequirements,
    ) -> str | None:
        min_years = (
            requirements.experience.min_years
        )

        max_years = (
            requirements.experience.max_years
        )

        if min_years is None:
            return None

        if max_years is not None:
            return (
                f"{JobRequirementsMapper._format_number(min_years)}"
                f" à "
                f"{JobRequirementsMapper._format_number(max_years)}"
                f" ans"
            )

        return (
            f"{JobRequirementsMapper._format_number(min_years)}"
            f" ans"
        )

    @staticmethod
    def _format_number(
        value: float,
    ) -> str:
        if value.is_integer():
            return str(int(value))

        return str(value)
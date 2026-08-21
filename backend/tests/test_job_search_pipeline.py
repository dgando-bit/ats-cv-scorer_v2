from app.models.cv import CV
from app.models.job import JobOffer
from app.models.job_relevance import (
    JobRelevanceEvaluation,
)
from app.models.job_requirements import (
    ExperienceRequirement,
    JobRequirements,
)
from app.services.matching.job_search_pipeline import (
    JobSearchPipeline,
)


class FakeProvider:
    def search_jobs(
        self,
        keywords,
        location=None,
        insee_code=None,
        limit=50,
    ):
        return [
            JobOffer(
                id="1",
                title="Frontend Engineer",
                description=(
                    "React frontend development"
                ),
                source="france_travail",
            ),
            JobOffer(
                id="2",
                title="Software Engineer",
                description=(
                    "REST APIs and backend services"
                ),
                source="france_travail",
            ),
        ]


class FakeSemanticService:
    def similarities(
        self,
        query,
        documents,
    ):
        scores = []

        for document in documents:
            if "Software Engineer" in document:
                scores.append(
                    0.80
                )
            else:
                scores.append(
                    0.90
                )

        return scores


class FakeRelevanceEvaluator:
    def evaluate_many(
        self,
        query,
        jobs,
    ):
        evaluations = []

        for job in jobs:
            if job.id == "2":
                evaluations.append(
                    JobRelevanceEvaluation(
                        relevance=0.95,
                        reason="Backend role.",
                    )
                )
            else:
                evaluations.append(
                    JobRelevanceEvaluation(
                        relevance=0.10,
                        reason="Frontend role.",
                    )
                )

        return evaluations


class FakeRequirementsBatchExtractor:
    def extract(
        self,
        jobs,
    ):
        results = []

        for job in jobs:
            if job.id == "2":
                results.append(
                    JobRequirements(
                        hard_skills=[
                            "Python",
                        ],
                        tools=[],
                        soft_skills=[],
                        languages=[],
                        experience=(
                            ExperienceRequirement(
                                min_years=2,
                                max_years=4,
                                context=(
                                    "Backend development"
                                ),
                            )
                        ),
                        education_level="Bac+5",
                        certifications=[],
                        responsibilities=[
                            "Develop backend services",
                        ],
                    )
                )

                continue

            results.append(
                JobRequirements(
                    hard_skills=[
                        "Frontend development",
                    ],
                    tools=[
                        "React",
                    ],
                    soft_skills=[],
                    languages=[],
                    experience=(
                        ExperienceRequirement(
                            min_years=None,
                            max_years=None,
                            context=None,
                        )
                    ),
                    education_level=None,
                    certifications=[],
                    responsibilities=[
                        "Develop user interfaces",
                    ],
                )
            )

        return results


class FailingRequirementsBatchExtractor:
    def extract(
        self,
        jobs,
    ):
        raise RuntimeError(
            "Groq unavailable"
        )


class FakeExtractor:
    """
    Fallback lexical extractor.

    La signature correspond à celle du vrai
    JobOfferExtractor.extract().
    """

    def extract(
        self,
        text,
        *,
        title=None,
        company=None,
        location=None,
        contract_type=None,
        job_id=None,
        source=None,
        source_url=None,
    ):
        return JobOffer(
            id=job_id,
            title=title or "",
            company=company,
            location=location,
            contract_type=contract_type,
            description=text,
            skills=[
                "fallback-skill",
            ],
            tools=[],
            soft_skills=[],
            languages=[],
            experience_required=None,
            education_required=None,
            source=source,
            source_url=source_url,
        )


class FakeMatchingEngine:
    def match(
        self,
        cv,
        job,
    ):
        from app.models.match import (
            MatchDetails,
            MatchResult,
        )

        score = (
            90.0
            if job.id == "2"
            else 40.0
        )

        return MatchResult(
            score=score,
            details=MatchDetails(
                skills=score,
                tools=0.0,
                languages=0.0,
                experience=0.0,
                education=0.0,
            ),
            matched_skills=[],
            missing_skills=[],
            matched_tools=[],
            missing_tools=[],
            matched_languages=[],
            missing_languages=[],
        )


class FakeExplanationService:
    def explain(
        self,
        job,
        match,
    ):
        from app.models.match import (
            MatchExplanation,
        )

        return MatchExplanation(
            summary="Test",
            strengths=[],
            weaknesses=[],
            recommendations=[],
        )


def make_cv() -> CV:
    return CV(
        candidate_name="John Doe",
        title="Backend Developer",
        skills=[],
        tools=[],
        languages=[],
        experiences=[],
        education=[],
    )


def test_job_search_pipeline_uses_llm_relevance():
    pipeline = JobSearchPipeline(
        provider=FakeProvider(),
        relevance_evaluator=(
            FakeRelevanceEvaluator()
        ),
        semantic_service=(
            FakeSemanticService()
        ),
        job_offer_extractor=(
            FakeExtractor()
        ),
        requirements_batch_extractor=(
            FakeRequirementsBatchExtractor()
        ),
        matching_engine=(
            FakeMatchingEngine()
        ),
        explanation_service=(
            FakeExplanationService()
        ),
    )

    result = pipeline.search_and_rank(
        cv=make_cv(),
        keywords="développeur backend",
        provider_limit=10,
        retrieval_top_k=10,
        final_limit=2,
    )

    assert len(
        result.jobs
    ) == 2

    # Le retrieval sémantique place volontairement
    # Frontend devant.
    #
    # Le reranking doit remettre le backend devant.
    assert (
        result.jobs[0].job.id
        == "2"
    )

    assert (
        result.jobs[0].relevance_score
        == 0.95
    )

    assert (
        result.jobs[0].semantic_score
        == 0.80
    )

    assert (
        result.jobs[0].match.score
        == 90.0
    )

    # Vérification du mapping
    # JobRequirements -> JobOffer.
    assert (
        result.jobs[0]
        .job
        .experience_required
        == "2 à 4 ans"
    )

    assert (
        result.jobs[0]
        .job
        .education_required
        == "Bac+5"
    )

    assert (
        result.jobs[0]
        .job
        .skills
        == ["Python"]
    )


def test_job_search_pipeline_falls_back_to_lexical_extractor():
    pipeline = JobSearchPipeline(
        provider=FakeProvider(),
        relevance_evaluator=(
            FakeRelevanceEvaluator()
        ),
        semantic_service=(
            FakeSemanticService()
        ),
        job_offer_extractor=(
            FakeExtractor()
        ),
        requirements_batch_extractor=(
            FailingRequirementsBatchExtractor()
        ),
        matching_engine=(
            FakeMatchingEngine()
        ),
        explanation_service=(
            FakeExplanationService()
        ),
    )

    result = pipeline.search_and_rank(
        cv=make_cv(),
        keywords="développeur backend",
        provider_limit=10,
        retrieval_top_k=10,
        final_limit=1,
    )

    assert len(
        result.jobs
    ) == 1

    assert (
        result.jobs[0].job.id
        == "2"
    )

    # Cette skill prouve que le fallback
    # lexical a bien été utilisé.
    assert (
        result.jobs[0]
        .job
        .skills
        == ["fallback-skill"]
    )


def test_job_search_pipeline_respects_final_limit():
    pipeline = JobSearchPipeline(
        provider=FakeProvider(),
        relevance_evaluator=(
            FakeRelevanceEvaluator()
        ),
        semantic_service=(
            FakeSemanticService()
        ),
        job_offer_extractor=(
            FakeExtractor()
        ),
        requirements_batch_extractor=(
            FakeRequirementsBatchExtractor()
        ),
        matching_engine=(
            FakeMatchingEngine()
        ),
        explanation_service=(
            FakeExplanationService()
        ),
    )

    result = pipeline.search_and_rank(
        cv=make_cv(),
        keywords="développeur backend",
        provider_limit=10,
        retrieval_top_k=10,
        final_limit=1,
    )

    assert len(
        result.jobs
    ) == 1

    assert (
        result.jobs[0].job.id
        == "2"
    )
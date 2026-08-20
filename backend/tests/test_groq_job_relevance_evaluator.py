from types import SimpleNamespace

from app.models.job import JobOffer
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)


class FakeCompletions:

    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=(
                            '{"relevance": 0.92, '
                            '"reason": "The job focuses '
                            'on backend development."}'
                        )
                    )
                )
            ]
        )


class FakeClient:

    def __init__(self):
        self.chat = SimpleNamespace(
            completions=FakeCompletions()
        )


def make_evaluator():
    return GroqJobRelevanceEvaluator(
        client=FakeClient(),
        model="fake-model",
    )


def test_evaluate_job_relevance():
    evaluator = make_evaluator()

    job = JobOffer(
        title="Software Engineer",
        description=(
            "Development of REST APIs, "
            "microservices and server-side "
            "services."
        ),
        skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
        ],
    )

    result = evaluator.evaluate(
        query="développeur backend",
        job=job,
    )

    assert result.relevance == 0.92
    assert result.reason


def test_empty_query():
    evaluator = make_evaluator()

    job = JobOffer(
        title="Software Engineer",
        description="Backend development",
        skills=["Python"],
    )

    result = evaluator.evaluate(
        query="",
        job=job,
    )

    assert result.relevance == 0.0
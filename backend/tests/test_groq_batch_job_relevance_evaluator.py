import json
from types import SimpleNamespace

from app.models.job import JobOffer
from app.services.llm.groq_job_relevance_evaluator import (
    GroqJobRelevanceEvaluator,
)


class FakeCompletions:
    def __init__(self):
        self.call_count = 0
        self.kwargs = None

    def create(
        self,
        **kwargs,
    ):
        self.call_count += 1
        self.kwargs = kwargs

        content = json.dumps(
            {
                "evaluations": [
                    {
                        "candidate_id": "0",
                        "relevance": 0.20,
                        "reason": (
                            "Frontend role."
                        ),
                    },
                    {
                        "candidate_id": "1",
                        "relevance": 0.95,
                        "reason": (
                            "Backend role."
                        ),
                    },
                ]
            }
        )

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=(
                        SimpleNamespace(
                            content=content
                        )
                    )
                )
            ]
        )


class FakeClient:
    def __init__(self):
        self.completions = (
            FakeCompletions()
        )

        self.chat = SimpleNamespace(
            completions=(
                self.completions
            )
        )


def test_evaluate_many_uses_single_request():
    client = FakeClient()

    evaluator = (
        GroqJobRelevanceEvaluator(
            client=client,
            model="fake-model",
        )
    )

    jobs = [
        JobOffer(
            id="1",
            title="Frontend Engineer",
            description=(
                "React interfaces."
            ),
        ),
        JobOffer(
            id="2",
            title="Backend Engineer",
            description=(
                "REST APIs and services."
            ),
        ),
    ]

    results = evaluator.evaluate_many(
        query="backend developer",
        jobs=jobs,
    )

    assert (
        client.completions.call_count
        == 1
    )

    assert len(results) == 2

    assert (
        results[0].relevance
        == 0.20
    )

    assert (
        results[1].relevance
        == 0.95
    )


def test_evaluate_many_preserves_original_order():
    client = FakeClient()

    evaluator = (
        GroqJobRelevanceEvaluator(
            client=client,
            model="fake-model",
        )
    )

    jobs = [
        JobOffer(
            title="Frontend Engineer",
            description="React.",
        ),
        JobOffer(
            title="Backend Engineer",
            description="Python.",
        ),
    ]

    results = evaluator.evaluate_many(
        query="backend",
        jobs=jobs,
    )

    assert [
        result.relevance
        for result in results
    ] == [
        0.20,
        0.95,
    ]


def test_evaluate_many_empty_jobs():
    client = FakeClient()

    evaluator = (
        GroqJobRelevanceEvaluator(
            client=client,
            model="fake-model",
        )
    )

    results = evaluator.evaluate_many(
        query="backend",
        jobs=[],
    )

    assert results == []

    assert (
        client.completions.call_count
        == 0
    )
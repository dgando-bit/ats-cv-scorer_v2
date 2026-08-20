from app.models.cv import (
    CV,
    Education,
    Experience,
)
from app.services.matching.candidate_language_resolver import (
    CandidateLanguageResolver,
)
from app.services.matching.language_normalizer import (
    LanguageNormalizer,
)


def test_preserves_explicit_languages():
    cv = CV(
        languages=[
            "Anglais (B2)",
            "LSF (C2)",
        ]
    )

    result = (
        CandidateLanguageResolver()
        .resolve(cv)
    )

    assert result == [
        "Anglais (B2)",
        "LSF (C2)",
    ]


def test_infers_french_without_level():
    cv = CV(
        title="Machine Learning Engineer",
        experiences=[
            Experience(
                company="Entreprise",
                role="Développeur Back-end",
                description=[
                    "Développement d'applications",
                    "Conception de systèmes",
                ],
            ),
        ],
        education=[
            Education(
                institution=(
                    "Université française"
                ),
                degree=(
                    "Master informatique"
                ),
            ),
        ],
        languages=[
            "Anglais (B2)",
        ],
    )

    result = (
        CandidateLanguageResolver()
        .resolve(cv)
    )

    assert (
        "Anglais (B2)"
        in result
    )

    assert (
        "Français"
        in result
    )

    # On ne doit surtout pas inventer
    # de niveau de français.
    assert not any(
        language.startswith(
            "Français ("
        )
        for language in result
    )


def test_does_not_duplicate_explicit_french():
    cv = CV(
        experiences=[
            Experience(
                role="Développeur",
                description=[
                    "Développement d'applications",
                    "Conception de projets",
                ],
            ),
        ],
        languages=[
            "French (B2)",
        ],
    )

    result = (
        CandidateLanguageResolver()
        .resolve(cv)
    )

    french_languages = [
        language
        for language in result
        if (
            LanguageNormalizer
            .normalize(language)
            .language
            == "français"
        )
    ]

    assert len(
        french_languages
    ) == 1

    assert result == [
        "French (B2)",
    ]


def test_does_not_infer_french_from_english_cv():
    cv = CV(
        title="Marketing Manager",
        experiences=[
            Experience(
                role="Marketing Manager",
                description=[
                    (
                        "Managed marketing "
                        "campaigns."
                    ),
                    (
                        "Developed product "
                        "strategy."
                    ),
                ],
            ),
        ],
        education=[
            Education(
                institution=(
                    "Wardiere University"
                ),
                degree=(
                    "Master of Business "
                    "Management"
                ),
            ),
        ],
        languages=[
            "English (Fluent)",
        ],
    )

    result = (
        CandidateLanguageResolver()
        .resolve(cv)
    )

    assert result == [
        "English (Fluent)",
    ]


def test_french_inference_requires_enough_evidence():
    cv = CV(
        title="Software Engineer",
        experiences=[
            Experience(
                role="Développeur",
                description=[
                    "Backend development",
                ],
            ),
        ],
        languages=[
            "English (B2)",
        ],
    )

    result = (
        CandidateLanguageResolver()
        .resolve(cv)
    )

    assert result == [
        "English (B2)",
    ]
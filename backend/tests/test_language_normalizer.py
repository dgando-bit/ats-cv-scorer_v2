from app.services.matching.language_normalizer import (
    LanguageNormalizer,
)


def test_normalize_french_language():
    result = LanguageNormalizer.normalize(
        "French (B2)"
    )

    assert result.language == "français"
    assert result.level == "B2"


def test_normalize_english_language():
    result = LanguageNormalizer.normalize(
        "Anglais (C1)"
    )

    assert result.language == "anglais"
    assert result.level == "C1"


def test_normalize_fluent_level():
    result = LanguageNormalizer.normalize(
        "English (Fluent)"
    )

    assert result.language == "anglais"
    assert result.level == "C1"


def test_normalize_native_level():
    result = LanguageNormalizer.normalize(
        "French (native)"
    )

    assert result.language == "français"
    assert result.level == "C2"


def test_normalize_lsf():
    result = LanguageNormalizer.normalize(
        "LSF (C2)"
    )

    assert result.language == "lsf"
    assert result.level == "C2"


def test_language_without_level():
    result = LanguageNormalizer.normalize(
        "English"
    )

    assert result.language == "anglais"
    assert result.level is None
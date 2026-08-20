import re
from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizedLanguage:
    language: str
    level: str | None = None


class LanguageNormalizer:
    LANGUAGE_ALIASES = {
        "anglais": "anglais",
        "english": "anglais",

        "français": "français",
        "francais": "français",
        "french": "français",

        "allemand": "allemand",
        "german": "allemand",

        "espagnol": "espagnol",
        "spanish": "espagnol",

        "lsf": "lsf",
        "langue des signes française": "lsf",
        "langue des signes francaise": "lsf",
    }

    LEVEL_ALIASES = {
        "a1": "A1",
        "a2": "A2",
        "b1": "B1",
        "b2": "B2",
        "c1": "C1",
        "c2": "C2",

        "native": "C2",
        "natif": "C2",
        "native speaker": "C2",
        "bilingue": "C2",

        "fluent": "C1",
        "courant": "C1",

        "professional": "B2",
        "professionnel": "B2",
        "professional working proficiency": "B2",

        "intermediate": "B1",
        "intermédiaire": "B1",
        "intermediaire": "B1",

        "beginner": "A1",
        "débutant": "A1",
        "debutant": "A1",
    }

    LEVEL_VALUES = {
        "A1": 1,
        "A2": 2,
        "B1": 3,
        "B2": 4,
        "C1": 5,
        "C2": 6,
    }

    @classmethod
    def normalize(
        cls,
        value: str,
    ) -> NormalizedLanguage:
        value = value.strip()

        match = re.match(
            r"^\s*(.*?)\s*"
            r"(?:\((.*?)\))?\s*$",
            value,
        )

        if not match:
            return NormalizedLanguage(
                language=value.lower(),
            )

        raw_language = (
            match.group(1)
            .strip()
            .lower()
        )

        raw_level = (
            match.group(2)
            .strip()
            .lower()
            if match.group(2)
            else None
        )

        language = cls.LANGUAGE_ALIASES.get(
            raw_language,
            raw_language,
        )

        level = None

        if raw_level:
            level = cls.LEVEL_ALIASES.get(
                raw_level,
                raw_level.upper(),
            )

        return NormalizedLanguage(
            language=language,
            level=level,
        )

    @classmethod
    def level_value(
        cls,
        level: str | None,
    ) -> int | None:
        if not level:
            return None

        return cls.LEVEL_VALUES.get(
            level
        )
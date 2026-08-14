import re


class RegexExtractor:
    """Extract highly structured information from resume text."""

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    PHONE_PATTERN = re.compile(
        r"""
        (?<!\w)
        (
            # Format international / français
            \+?\d{1,3}
            (?:[\s.\-]\d{1,4}){3,5}

            |

            # Format US classique
            \d{3}-\d{3}-\d{4}
        )
        (?!\w)
        """,
        re.VERBOSE,
    )

    DATE_RANGE_PATTERN = re.compile(
        r"\b(19|20)\d{2}\s*[-–—]\s*(?:(19|20)\d{2}|présent|aujourd'hui|actuel)\b",
        re.IGNORECASE,
    )

    YEAR_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b"
    )

    URL_PATTERN = re.compile(
        r"\b(?:https?://|www\.)[^\s]+\b",
        re.IGNORECASE,
    )

    def extract(self, text: str) -> dict:
        return {
            "emails": self._extract(self.EMAIL_PATTERN, text),
            "phones": self._extract(self.PHONE_PATTERN, text),
            "date_ranges": self._extract(
                self.DATE_RANGE_PATTERN, text
            ),
            "urls": self._extract(self.URL_PATTERN, text),
        }

    @staticmethod
    def _extract(pattern: re.Pattern, text: str) -> list[str]:
        return [match.group(0).strip() for match in pattern.finditer(text)]
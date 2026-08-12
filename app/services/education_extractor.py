import re

from app.models.cv import Education
from app.services.layout_extractor import TextBlock


class EducationExtractor:

    YEAR_RANGE_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2})\b"
    )

    YEAR_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\b"
    )

    def extract(
        self,
        blocks: list[TextBlock],
    ) -> list[Education]:

        if not blocks:
            return []

        # On conserve les lignes du PDF.
        lines: list[str] = []

        for block in blocks:
            for line in block.text.splitlines():
                line = line.strip()

                if line:
                    lines.append(line)

        educations: list[Education] = []

        i = 0

        while i < len(lines):

            line = lines[i]

            # Une formation commence par une année.
            if not self._extract_year(line):
                i += 1
                continue

            year = self._extract_year(line)

            # Collecte toutes les lignes jusqu'à la prochaine année.
            education_lines = [line]
            i += 1

            while i < len(lines):

                next_line = lines[i]

                if self._extract_year(next_line):
                    break

                education_lines.append(next_line)
                i += 1

            degree, institution = self._parse_education(
                education_lines
            )

            educations.append(
                Education(
                    institution=institution,
                    degree=degree,
                    year=year,
                )
            )

        return educations

    def _parse_education(
        self,
        lines: list[str],
    ) -> tuple[str, str | None]:

        text = " ".join(lines)

        # ---------------------------------------------------------
        # 1. Extraire le diplôme entre « »
        # ---------------------------------------------------------

        quoted_match = re.search(
            r"«\s*(.*?)\s*»",
            text,
        )

        if quoted_match:

            quoted_degree = quoted_match.group(1).strip()

            # Cas normal :
            #
            # 2025-2026 : « Expert en Ingénierie de l’IA »
            #
            # => Expert en Ingénierie de l’IA
            #
            # Mais pour :
            #
            # 2001: BTS « Informatique Industrielle »
            #
            # => BTS « Informatique Industrielle »
            before_quote = text[:quoted_match.start()].strip()

            if re.search(
                r"\bBTS\b",
                before_quote,
                flags=re.IGNORECASE,
            ):
                degree = (
                    before_quote
                    + " "
                    + text[
                        quoted_match.start():
                        quoted_match.end()
                    ]
                ).strip()

            else:
                degree = quoted_degree

        else:
            degree = text

        # ---------------------------------------------------------
        # 2. Nettoyer l'année
        # ---------------------------------------------------------

        degree = self.YEAR_RANGE_PATTERN.sub("", degree)
        degree = self.YEAR_PATTERN.sub("", degree)

        degree = re.sub(
            r"^\s*:\s*",
            "",
            degree,
        )

        # ---------------------------------------------------------
        # 3. Supprimer les informations de niveau
        # ---------------------------------------------------------

        degree = re.sub(
            r"\s*[–—-]\s*Niveau\s+\d+.*$",
            "",
            degree,
            flags=re.IGNORECASE,
        )

        degree = degree.strip()

        # ---------------------------------------------------------
        # 4. Trouver l'établissement
        # ---------------------------------------------------------

        institution = self._extract_institution(
            lines,
            text,
            degree,
        )

        return degree, institution

    def _extract_institution(
        self,
        lines: list[str],
        text: str,
        degree: str,
    ) -> str | None:

        # L'établissement apparaît généralement après
        # les informations concernant le diplôme.

        # On cherche la fin du diplôme / niveau.
        level_match = re.search(
            r"\(BAC\+\d+(?:/\d+)?\)",
            text,
            flags=re.IGNORECASE,
        )

        if level_match:
            institution = text[level_match.end():].strip()

            if institution:
                return self._clean_institution(institution)

        # Cas BTS sans niveau :
        #
        # 2001: BTS « Informatique Industrielle »
        # Lycée ORT Montreuil 93

        quoted_match = re.search(
            r"«\s*.*?\s*»",
            text,
        )

        if quoted_match:
            institution = text[quoted_match.end():].strip()

            # Si le texte restant contient le début du diplôme,
            # on essaie de le supprimer.
            institution = re.sub(
                r"^.*?\)\s*",
                "",
                institution,
            ).strip()

            if institution:
                return self._clean_institution(institution)

        # Fallback : chercher une ligne qui ne ressemble
        # pas au diplôme.
        if len(lines) >= 2:
            candidate = lines[-1]

            if not self._looks_like_degree(candidate):
                return self._clean_institution(candidate)

        return None

    @staticmethod
    def _looks_like_degree(text: str) -> bool:
        return bool(
            re.search(
                r"niveau\s+\d+|BAC\+\d+|BTS|licence|master|ingénieur",
                text,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _clean_institution(text: str) -> str:

        text = text.strip()

        # Supprime ponctuation finale.
        text = re.sub(
            r"[.,;]+$",
            "",
            text,
        )

        return text.strip()

    def _extract_year(
        self,
        text: str,
    ) -> str | None:

        range_match = self.YEAR_RANGE_PATTERN.search(text)

        if range_match:
            return (
                f"{range_match.group(1)}-"
                f"{range_match.group(2)}"
            )

        year_match = self.YEAR_PATTERN.search(text)

        if year_match:
            return year_match.group(1)

        return None
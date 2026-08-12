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

    # Un début de formation est identifié par une année en début de texte
    EDUCATION_START_PATTERN = re.compile(
        r"(?<!\d)\b(?:19|20)\d{2}(?:\s*[-–—]\s*(?:19|20)\d{2})?\s*[:\-]?"
    )

    def extract(
        self,
        blocks: list[TextBlock],
    ) -> list[Education]:

        if not blocks:
            return []

        # ---------------------------------------------------------
        # 1. Concaténer les blocs
        # ---------------------------------------------------------
        #
        # Un TextBlock peut contenir plusieurs formations.
        #
        # Exemple réel :
        #
        # Mines Paris...
        # 2018 : « Concepteur-Développeur...
        #
        # On conserve un espace entre les blocs pour éviter de
        # coller artificiellement les mots.
        # ---------------------------------------------------------

        text = " ".join(
            block.text.strip()
            for block in blocks
            if block.text.strip()
        )

        text = self._normalize_text(text)

        # ---------------------------------------------------------
        # 2. Découper le texte à chaque nouvelle année
        # ---------------------------------------------------------

        matches = list(
            self.EDUCATION_START_PATTERN.finditer(text)
        )

        if not matches:
            return []

        educations: list[Education] = []

        for index, match in enumerate(matches):

            start = match.start()

            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            segment = text[start:end].strip()

            education = self._parse_segment(segment)

            if education:
                educations.append(education)

        return educations

    # ---------------------------------------------------------
    # Parsing d'une formation
    # ---------------------------------------------------------

    def _parse_segment(
        self,
        text: str,
    ) -> Education | None:

        year = self._extract_year(text)

        if not year:
            return None

        # Supprimer l'année et les deux-points
        content = self._remove_year(text).strip()

        degree, institution = self._split_degree_institution(
            content
        )

        return Education(
            institution=institution,
            degree=degree,
            year=year,
        )

    # ---------------------------------------------------------
    # Extraction année
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Suppression année
    # ---------------------------------------------------------

    def _remove_year(
        self,
        text: str,
    ) -> str:

        text = self.YEAR_RANGE_PATTERN.sub(
            "",
            text,
            count=1,
        )

        text = self.YEAR_PATTERN.sub(
            "",
            text,
            count=1,
        )

        return (
            text
            .replace(":", " ")
            .strip()
        )

    # ---------------------------------------------------------
    # Séparation diplôme / établissement
    # ---------------------------------------------------------

    def _split_degree_institution(
        self,
        text: str,
    ) -> tuple[str, str | None]:

        text = self._normalize_text(text)

        # -----------------------------------------------------
        # Cas avec des guillemets :
        #
        # « Expert en Ingénierie de l’IA » – Niveau 7 (BAC+5)
        # Mines Paris – PSL Executive Education
        #
        # ou :
        #
        # BTS « Informatique Industrielle »
        # Lycée ORT Montreuil 93
        # -----------------------------------------------------

        quote_match = re.search(
            r"«\s*(.*?)\s*»",
            text,
        )

        if quote_match:

            quoted_degree = quote_match.group(1).strip()

            # Texte avant les guillemets
            prefix = text[:quote_match.start()].strip()

            # Texte après les guillemets
            suffix = text[quote_match.end():].strip()

            # ---------------------------------------------
            # Cas BTS :
            #
            # BTS « Informatique Industrielle »
            #
            # Le BTS fait partie du diplôme.
            # ---------------------------------------------

            if re.search(
                r"\bBTS\b",
                prefix,
                flags=re.IGNORECASE,
            ):
                degree = (
                    f"{prefix} « {quoted_degree} »"
                ).strip()
            else:
                degree = quoted_degree

            # ---------------------------------------------
            # Supprimer les informations de niveau
            #
            # – Niveau 7 (BAC+5)
            # – Niveau 6 (BAC+3/4)
            # ---------------------------------------------

            suffix = re.sub(
                r"^\s*[–-]\s*Niveau\s+\d+"
                r"(?:\s*\([^)]*\))?",
                "",
                suffix,
                flags=re.IGNORECASE,
            ).strip()

            # Supprimer éventuellement :
            # (BAC+5), (BAC+3/4)
            suffix = re.sub(
                r"^\s*\([^)]*\)",
                "",
                suffix,
            ).strip()

            institution = self._clean_institution(suffix)

            return degree, institution

        # -----------------------------------------------------
        # Fallback sans guillemets
        # -----------------------------------------------------

        # Exemple :
        # Diplôme – Niveau 7 (BAC+5) Institution
        level_match = re.search(
            r"\s*[–-]\s*Niveau\s+\d+"
            r"(?:\s*\([^)]*\))?",
            text,
            flags=re.IGNORECASE,
        )

        if level_match:

            degree = text[:level_match.start()].strip()
            institution = text[level_match.end():].strip()

            return (
                self._clean_degree(degree),
                self._clean_institution(institution),
            )

        # -----------------------------------------------------
        # Aucun séparateur identifiable.
        #
        # On garde tout comme diplôme.
        # -----------------------------------------------------

        return (
            self._clean_degree(text),
            None,
        )

    # ---------------------------------------------------------
    # Nettoyage diplôme
    # ---------------------------------------------------------

    @staticmethod
    def _clean_degree(text: str) -> str:

        return (
            text
            .strip()
            .rstrip(".")
            .strip()
        )

    # ---------------------------------------------------------
    # Nettoyage établissement
    # ---------------------------------------------------------

    @staticmethod
    def _clean_institution(
        text: str,
    ) -> str | None:

        text = text.strip()

        if not text:
            return None

        # Supprimer les espaces multiples
        text = re.sub(r"\s+", " ", text)

        # Supprimer la ponctuation finale
        text = text.rstrip(" .")

        return text or None

    # ---------------------------------------------------------
    # Normalisation
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_text(text: str) -> str:

        # Les PDF contiennent souvent des retours à la ligne
        # artificiels au milieu des phrases.
        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()
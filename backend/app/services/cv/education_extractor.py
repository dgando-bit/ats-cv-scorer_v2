import re

from app.models.cv import Education
from app.services.cv.layout_extractor import TextBlock


class EducationExtractor:
    """Extract education entries from CV text blocks."""

    YEAR_RANGE_PATTERN = re.compile(
        r"\b("
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\s+)?"
        r"(?:19|20)\d{2}"
        r")"
        r"\s*[-–—]\s*"
        r"("
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\s+)?"
        r"(?:19|20)\d{2}"
        r")\b",
        re.IGNORECASE,
    )

    YEAR_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\b"
    )

    LEVEL_PATTERN = re.compile(
        r"\s*[–—-]\s*Niveau\s+\d+"
        r"(?:\s*\(BAC\+\d+(?:/\d+)?\))?"
        r"|\s*\(BAC\+\d+(?:/\d+)?\)",
        flags=re.IGNORECASE,
    )

    def extract(
        self,
        blocks: list[TextBlock],
    ) -> list[Education]:

        if not blocks:
            return []

        # ---------------------------------------------------------
        # 1. Conserver les lignes du PDF
        # ---------------------------------------------------------

        lines: list[str] = []

        for block in blocks:
            for line in block.text.splitlines():
                line = line.strip()

                if line:
                    lines.append(line)

        educations: list[Education] = []

        i = 0

        # ---------------------------------------------------------
        # 2. Parcourir les lignes et détecter les années
        # ---------------------------------------------------------

        while i < len(lines):

            line = lines[i]

            year = self._extract_year(line)

            if not year:
                i += 1
                continue

            # Une formation commence avec cette ligne.
            education_lines = [line]
            i += 1

            # Toutes les lignes suivantes appartiennent à cette
            # formation jusqu'à la prochaine année.
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

    # =============================================================
    # Parsing d'une formation
    # =============================================================

    def _parse_education(
            self,
            lines: list[str],
    ) -> tuple[str, str | None]:

        if not lines:
            return "", None

        # ---------------------------------------------------------
        # 1. Supprimer l'année du début
        # ---------------------------------------------------------

        content_lines = list(lines)

        first_line = content_lines[0]

        first_line = self.YEAR_RANGE_PATTERN.sub(
            "",
            first_line,
        )

        first_line = self.YEAR_PATTERN.sub(
            "",
            first_line,
        )

        first_line = re.sub(
            r"^\s*:\s*",
            "",
            first_line,
        ).strip()

        if first_line:
            content_lines[0] = first_line
        else:
            content_lines = content_lines[1:]

        content_lines = [
            line.strip()
            for line in content_lines
            if line.strip()
        ]

        if not content_lines:
            return "", None

        # ---------------------------------------------------------
        # 2. Retirer les métadonnées
        #
        # GPA, moyenne, mention...
        # ---------------------------------------------------------

        content_lines = [
            line
            for line in content_lines
            if not self._looks_like_metadata(line)
        ]

        if not content_lines:
            return "", None

        # ---------------------------------------------------------
        # 3. Cas diplôme entre « »
        #
        # On conserve le comportement historique.
        # ---------------------------------------------------------

        full_text = " ".join(content_lines)

        quoted_match = re.search(
            r"«\s*(.*?)\s*»",
            full_text,
        )

        if quoted_match:

            quoted_degree = quoted_match.group(1).strip()

            before_quote = full_text[
                :quoted_match.start()
            ].strip()

            if re.search(
                    r"\bBTS\b",
                    before_quote,
                    flags=re.IGNORECASE,
            ):
                degree = (
                        before_quote
                        + " "
                        + full_text[
                            quoted_match.start():
                            quoted_match.end()
                        ]
                ).strip()
            else:
                degree = quoted_degree

            degree = self._clean_degree(
                degree
            )

            institution = (
                self._extract_institution_from_after_quote(
                    full_text[
                        quoted_match.end():
                    ].strip()
                )
            )

            if institution is None:
                institution = self._find_institution(
                    content_lines,
                    degree,
                )

            return degree, institution

        # ---------------------------------------------------------
        # 4. Diplôme + établissement sur une même ligne
        #
        # Exemple :
        # Master Data Science – Université Paris-Saclay
        # ---------------------------------------------------------

        if len(content_lines) == 1:

            same_line = self._split_degree_institution(
                content_lines[0]
            )

            if same_line:
                return same_line

        # ---------------------------------------------------------
        # 4. Détecter l'établissement
        # ---------------------------------------------------------

        institution_index = None

        for index, line in enumerate(content_lines):

            if self._looks_like_institution(line):
                institution_index = index
                break

        if institution_index is not None:
            institution = self._clean_institution(
                content_lines[institution_index]
            )

            degree_lines = [
                line
                for index, line in enumerate(content_lines)
                if index != institution_index
            ]

            degree = self._clean_degree(
                " ".join(degree_lines)
            )

            return degree, institution

        # ---------------------------------------------------------
        # 5. Inférence générique sur deux lignes
        # ---------------------------------------------------------

        if len(content_lines) == 2:

            first = content_lines[0]
            second = content_lines[1]

            if (
                not self._looks_like_degree(first)
                and self._looks_like_degree(second)
            ):
                return (
                    self._clean_degree(second),
                    self._clean_institution(first),
                )

            if (
                self._looks_like_degree(first)
                and not self._looks_like_degree(second)
            ):
                return (
                    self._clean_degree(first),
                    self._clean_institution(second),
                )

            if self._looks_like_numeric_institution(first):
                return (
                    self._clean_degree(second),
                    self._clean_institution(first),
                )

        # ---------------------------------------------------------
        # 6. Ancien format :
        #
        # diplôme
        # établissement
        # ---------------------------------------------------------

        if len(content_lines) >= 2:

            first_content = content_lines[0]

            same_line = self._split_degree_institution(
                first_content
            )

            if same_line:
                return same_line

            degree = self._clean_degree(
                first_content
            )

            institution = self._find_institution(
                content_lines[1:],
                degree,
            )

            if institution:
                return degree, institution

        # ---------------------------------------------------------
        # 7. Une seule ligne
        # ---------------------------------------------------------

        single_line = content_lines[0]

        same_line = self._split_degree_institution(
            single_line
        )

        if same_line:
            return same_line

        return self._clean_degree(single_line), None

    # =============================================================
    # Séparer diplôme / établissement sur une même ligne
    # =============================================================

    def _split_degree_institution(
        self,
        text: str,
    ) -> tuple[str, str] | None:

        # Format :
        #
        # Master Data Science – Université Paris-Saclay
        #
        # On utilise un tiret long comme séparateur.
        match = re.search(
            r"\s+[–—]\s+",
            text,
        )

        if not match:
            return None

        degree = text[:match.start()].strip()
        institution = text[match.end():].strip()

        if not degree or not institution:
            return None

        # Attention :
        #
        # "Master Data Science – Niveau 7"
        #
        # ne doit PAS être interprété comme une institution.
        if re.match(
            r"^Niveau\s+\d+",
            institution,
            flags=re.IGNORECASE,
        ):
            return None

        degree = self._clean_degree(degree)

        institution = self._clean_institution(
            institution
        )

        return degree, institution

    # =============================================================
    # Nettoyage du diplôme
    # =============================================================

    def _clean_degree(
        self,
        degree: str,
    ) -> str:

        degree = degree.strip()

        # Supprimer l'année.
        degree = self.YEAR_RANGE_PATTERN.sub(
            "",
            degree,
        )

        degree = self.YEAR_PATTERN.sub(
            "",
            degree,
        )

        # Supprimer ":" au début.
        degree = re.sub(
            r"^\s*:\s*",
            "",
            degree,
        )

        # Supprimer les niveaux :
        #
        # – Niveau 7
        # – Niveau 7 (BAC+5)
        # (BAC+5)
        #
        degree = self.LEVEL_PATTERN.sub(
            "",
            degree,
        )

        degree = degree.strip(
            " \t–—-:"
        )

        return degree.strip()

    # =============================================================
    # Extraction de l'établissement après les guillemets
    # =============================================================

    def _extract_institution_from_after_quote(
        self,
        text: str,
    ) -> str | None:

        if not text:
            return None

        # Supprimer d'abord les informations de niveau.
        text = self.LEVEL_PATTERN.sub(
            "",
            text,
        )

        text = text.strip()

        if not text:
            return None

        return self._clean_institution(text)

    # =============================================================
    # Recherche de l'établissement
    # =============================================================

    def _find_institution(
        self,
        lines: list[str],
        degree: str,
    ) -> str | None:

        for line in lines:

            candidate = line.strip()

            if not candidate:
                continue

            # Une ligne ressemblant encore au diplôme
            # n'est probablement pas l'établissement.
            if self._looks_like_degree(candidate):
                continue

            # Supprimer les niveaux éventuels.
            candidate = self.LEVEL_PATTERN.sub(
                "",
                candidate,
            ).strip()

            if candidate:
                return self._clean_institution(
                    candidate
                )

        return None

    # =============================================================
    # Détection d'une ligne de diplôme
    # =============================================================

    @staticmethod
    def _looks_like_degree(text: str) -> bool:
        return bool(
            re.search(
                r"""
                \bmaster\b
                |\bbachelor\b
                |\blicence\b
                |\bbts\b
                |\bdut\b
                |\bbut\b
                |\bdegree\b
                |\bdipl[oô]me\b
                |\bing[eé]nieur\b
                |\bcertification\b
                |\bprogramme?\b
                |\bprogram\b
                """,
                text,
                flags=re.IGNORECASE | re.VERBOSE,
            )
        )

    # =============================================================
    # Nettoyage établissement
    # =============================================================

    @staticmethod
    def _clean_institution(
        text: str,
    ) -> str:

        text = text.strip()

        # Supprimer les informations de niveau qui auraient pu
        # rester devant l'établissement.
        text = re.sub(
            r"^[–—-]\s*Niveau\s+\d+"
            r"(?:\s*\(BAC\+\d+(?:/\d+)?\))?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Supprimer ponctuation finale.
        text = re.sub(
            r"[.,;]+$",
            "",
            text,
        )

        return text.strip()

    # =============================================================
    # Extraction année
    # =============================================================

    def _extract_year(
        self,
        text: str,
    ) -> str | None:

        range_match = self.YEAR_RANGE_PATTERN.search(
            text
        )

        if range_match:
            return (
                f"{range_match.group(1)}-"
                f"{range_match.group(2)}"
            )

        year_match = self.YEAR_PATTERN.search(
            text
        )

        if year_match:
            return year_match.group(1)

        return None

    @staticmethod
    def _looks_like_metadata(text: str) -> bool:
        return bool(
            re.search(
                r"\b(?:c?gpa|moyenne|mention)\b",
                text,
                flags=re.IGNORECASE,
            )
        )

    @staticmethod
    def _looks_like_institution(
            text: str,
    ) -> bool:
        """Heuristic: does this line look like an educational institution?"""

        normalized = text.lower()

        keywords = (
            "university",
            "université",
            "universite",
            "school",
            "école",
            "ecole",
            "institute",
            "institut",
            "academy",
            "académie",
            "academie",
            "college",
            "collège",
            "lycée",
            "lycee",
            "formation",
            "ifocop",
            "m2i",
            "mines paris",
        )

        return any(
            keyword in normalized
            for keyword in keywords
        )

    @staticmethod
    def _looks_like_numeric_institution(
            text: str,
    ) -> bool:
        """Detect institution names containing a meaningful number."""

        return bool(
            re.search(r"\d", text)
        )
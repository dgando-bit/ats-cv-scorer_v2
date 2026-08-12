import re

from app.models.cv import Education
from app.services.layout_extractor import TextBlock


class EducationExtractor:
    """Extract education entries from CV text blocks."""

    YEAR_RANGE_PATTERN = re.compile(
        r"\b((?:19|20)\d{2})\s*[-–—]\s*((?:19|20)\d{2})\b"
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
        # Cas particulier : année seule sur une ligne
        #
        # 2020
        # Master Intelligence Artificielle
        # Université Paris Cité
        # ---------------------------------------------------------

        first_line = lines[0]

        year_match = self.YEAR_RANGE_PATTERN.search(first_line)

        if year_match:
            content_first_line = (
                first_line[:year_match.start()]
                + first_line[year_match.end():]
            ).strip()
        else:
            year_match = self.YEAR_PATTERN.search(first_line)

            if year_match:
                content_first_line = (
                    first_line[:year_match.start()]
                    + first_line[year_match.end():]
                ).strip()
            else:
                content_first_line = first_line

        # Supprimer ":" qui peut rester après l'année.
        content_first_line = re.sub(
            r"^\s*:\s*",
            "",
            content_first_line,
        ).strip()

        remaining_lines = []

        if content_first_line:
            remaining_lines.append(content_first_line)

        remaining_lines.extend(lines[1:])

        # ---------------------------------------------------------
        # Si aucune ligne ne reste
        # ---------------------------------------------------------

        if not remaining_lines:
            return "", None

        # ---------------------------------------------------------
        # 1. Cas diplôme entre guillemets
        #
        # « Master Data Science » – Niveau 7
        # Université Paris-Saclay
        #
        # ou
        #
        # BTS « Informatique Industrielle »
        # Lycée ORT Montreuil 93
        # ---------------------------------------------------------

        full_text = " ".join(remaining_lines)

        quoted_match = re.search(
            r"«\s*(.*?)\s*»",
            full_text,
        )

        if quoted_match:

            quoted_degree = quoted_match.group(1).strip()

            before_quote = full_text[
                :quoted_match.start()
            ].strip()

            after_quote = full_text[
                quoted_match.end():
            ].strip()

            # Cas BTS :
            #
            # BTS « Informatique Industrielle »
            #
            # Le BTS fait partie du diplôme.
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

            # Supprimer le niveau.
            degree = self._clean_degree(degree)

            # Le reste peut contenir :
            #
            # – Niveau 7
            # Université Paris-Saclay
            #
            # ou directement :
            #
            # Université Paris-Saclay
            institution = self._extract_institution_from_after_quote(
                after_quote
            )

            # Si l'établissement n'a pas été trouvé après les
            # guillemets, chercher dans les lignes restantes.
            if institution is None:
                institution = self._find_institution(
                    remaining_lines,
                    degree,
                )

            return degree, institution

        # ---------------------------------------------------------
        # 2. Format classique :
        #
        # 2019 : Master Data Science
        # Université Paris-Saclay
        # ---------------------------------------------------------

        if len(remaining_lines) >= 2:

            first_content = remaining_lines[0]

            # Si le diplôme et l'établissement sont sur la même
            # ligne :
            #
            # Master Data Science – Université Paris-Saclay
            #
            same_line = self._split_degree_institution(
                first_content
            )

            if same_line:
                degree, institution = same_line
                return degree, institution

            # Sinon :
            #
            # Master Data Science
            # Université Paris-Saclay
            #
            degree = self._clean_degree(first_content)

            institution = self._find_institution(
                remaining_lines[1:],
                degree,
            )

            return degree, institution

        # ---------------------------------------------------------
        # 3. Tout est sur une seule ligne :
        #
        # 2021 : Master Data Science – Université Paris-Saclay
        # ---------------------------------------------------------

        single_line = remaining_lines[0]

        same_line = self._split_degree_institution(
            single_line
        )

        if same_line:
            return same_line

        # Sinon toute la ligne est considérée comme le diplôme.
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
    def _looks_like_degree(
        text: str,
    ) -> bool:

        return bool(
            re.search(
                r"""
                niveau\s+\d+
                |BAC\+\d+
                |\bBTS\b
                |\blicence\b
                |\bmaster\b
                |\bdoctorat\b
                |\bMBA\b
                |ingénieur
                |diplôme
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
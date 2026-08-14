import re

from app.models.cv import Experience
from app.services.layout_extractor import TextBlock


class ExperienceExtractor:
    """Extract professional experiences from PDF text blocks."""

    DATE_RANGE_PATTERN = re.compile(
        r"\(?\s*"
        r"("
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\s+)?"
        r"\d{4}"
        r")"
        r"\s*[-–—]\s*"
        r"("
        r"(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
        r"[a-z]*\s+)?"
        r"\d{4}"
        r"|présent"
        r"|present"
        r"|aujourd'hui"
        r")"
        r"\s*\)?",
        re.IGNORECASE,
    )

    # Liste de rôles connus. Les en-têtes de CV réels s'avèrent trop
    # ambigus pour être découpés de façon purement générique (ex:
    # "Adiict | Findeur | Cotep Développeur Informatique" où "|"
    # sépare des entreprises, pas le rôle de l'entreprise ; ou
    # "IA & Machine Learning Engineer Liora" sans aucun séparateur).
    # On garde donc une correspondance par rôle connu comme méthode
    # la plus fiable, mais elle est utilisée en dernier recours
    # après des règles génériques qui, elles, généralisent réellement
    # (voir _extract_role_company). Pour une vraie généralisation
    # au-delà de cette liste, brancher le modèle NER du projet
    # (app/services/resume_ner.py) est la prochaine étape recommandée.
    KNOWN_ROLES = [
        "IA & Machine Learning Engineer",
        "Développeur Back-end",
        "Développeur Informatique",
        "Responsable Informatique",
    ]

    # Mots-clés indiquant qu'un segment de texte désigne un
    # intitulé de poste plutôt qu'une entreprise. Utilisés
    # uniquement pour désambiguïser un segment ENTIER délimité par
    # un connecteur ou un séparateur (pas pour repérer une sous-
    # chaîne au milieu d'un texte plus long, ce qui serait trop
    # fragile).
    JOB_TITLE_KEYWORDS = [
        "engineer", "ingénieur", "ingenieur",
        "developer", "développeur", "developpeur",
        "manager", "responsable", "chef",
        "director", "directeur", "directrice",
        "consultant", "consultante",
        "analyst", "analyste",
        "architect", "architecte",
        "scientist", "scientifique",
        "chargé", "chargée", "charge",
        "technicien", "technicienne", "technician",
        "administrateur", "administratrice", "administrator",
        "lead", "stagiaire", "intern", "apprenti", "apprentie",
        "alternant", "alternante",
        "coordinateur", "coordinatrice", "coordinator",
        "spécialiste", "specialiste", "specialist",
        "product owner", "scrum master", "designer",
    ]

    # Connecteurs explicites et non-ambigus entre un intitulé de
    # poste et une entreprise, ex: "Data Engineer chez Liora",
    # "Developer at Acme". Ce cas généralise réellement, car le
    # connecteur lève l'ambiguïté sans avoir besoin de connaître
    # le rôle à l'avance.
    ROLE_COMPANY_CONNECTOR_PATTERN = re.compile(
        r"\s+(?:chez|at|pour|for)\s+",
        re.IGNORECASE,
    )

    def extract(
            self,
            blocks: list[TextBlock],
    ) -> list[Experience]:
        """Extract all experiences from ordered PDF blocks."""

        experiences: list[Experience] = []

        current_blocks: list[TextBlock] = []
        pending_blocks: list[TextBlock] = []

        for block in blocks:

            # ---------------------------------------------------------
            # Un bloc contenant une plage de dates marque le début
            # logique d'une expérience.
            #
            # Les blocs précédents peuvent contenir :
            #
            #   Airweb - Paragon ID
            #   Développeur Back-end
            #   (2021 - 2025)
            #
            # On les récupère donc depuis pending_blocks.
            # ---------------------------------------------------------

            if self._looks_like_experience_header(block.text):

                # Si une expérience était déjà en cours,
                # on la termine avant d'en commencer une nouvelle.
                if current_blocks:
                    experiences.append(
                        self._build_experience(current_blocks)
                    )

                current_blocks = [
                    *pending_blocks,
                    block,
                ]

                pending_blocks = []

                continue

            # ---------------------------------------------------------
            # Si aucune expérience n'a encore commencé, on conserve
            # les blocs dans pending_blocks.
            # ---------------------------------------------------------

            if not current_blocks:
                pending_blocks.append(block)
                continue

            # ---------------------------------------------------------
            # Sinon, le bloc appartient à l'expérience courante.
            # ---------------------------------------------------------

            current_blocks.append(block)

        # -------------------------------------------------------------
        # Dernière expérience
        # -------------------------------------------------------------

        if current_blocks:
            experiences.append(
                self._build_experience(current_blocks)
            )

        return experiences

    def _looks_like_experience_header(
        self,
        text: str,
    ) -> bool:
        """Return True when a block contains a date range."""

        return bool(
            self.DATE_RANGE_PATTERN.search(text)
        )

    def _build_experience(
            self,
            blocks: list[TextBlock],
    ) -> Experience:
        """Build an Experience from a group of related blocks."""

        # ---------------------------------------------------------
        # 1. Extraire les dates
        # ---------------------------------------------------------

        start_date: str | None = None
        end_date: str | None = None

        date_block_index: int | None = None

        for index, block in enumerate(blocks):
            match = self.DATE_RANGE_PATTERN.search(
                block.text
            )

            if match:
                start_date = match.group(1)
                end_date = match.group(2)
                date_block_index = index
                break

        # ---------------------------------------------------------
        # 2. Construire les blocs d'en-tête
        # ---------------------------------------------------------

        if date_block_index is not None:
            header_blocks = blocks[
                :date_block_index + 1
            ]
        else:
            header_blocks = blocks[:1]

        header = " ".join(
            block.text.strip()
            for block in header_blocks
            if block.text.strip()
        )

        # ---------------------------------------------------------
        # 3. Analyser la position de la date
        # ---------------------------------------------------------

        date_match = self.DATE_RANGE_PATTERN.search(
            header
        )

        before_date = ""
        after_date = ""

        if date_match:
            before_date = header[
                :date_match.start()
            ].strip()

            after_date = header[
                date_match.end():
            ].strip()

        header_without_date = (
            self.DATE_RANGE_PATTERN
            .sub("", header)
            .strip()
        )

        # ---------------------------------------------------------
        # 4. Extraire rôle + entreprise
        # ---------------------------------------------------------

        role: str | None = None
        company: str | None = None

        # Exemple :
        #
        # ACME Cloud (2022 - 2025) Cloud Architect
        if before_date and after_date:

            if self._looks_like_job_title(
                    after_date
            ):
                company = before_date
                role = after_date

        # Autres formats :
        #
        # Cloud Architect ACME Cloud (2022 - 2025)
        #
        # IA & Machine Learning Engineer
        # Liora (2025 - 2026)
        #
        # etc.
        if role is None or company is None:
            role, company = self._extract_role_company(
                header_without_date
            )

        # ---------------------------------------------------------
        # 5. Description
        # ---------------------------------------------------------

        description: list[str] = []

        if date_block_index is not None:
            description_blocks = blocks[
                date_block_index + 1:
            ]
        else:
            description_blocks = blocks[1:]

        for block in description_blocks:
            description.extend(
                self._normalize_description_block(
                    block.text
                )
            )

        return Experience(
            company=company,
            role=role,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

    @classmethod
    def _extract_role_company(
            cls,
            header: str,
    ) -> tuple[str | None, str | None]:
        """Extract role and company from an experience header.

        Strategy:
        1. Explicit connector ("chez", "at", "pour", "for").
        2. Multiline header:
           - detect the line that looks like a job title,
           - use the remaining line(s) as company.
        3. Known role fallback.
        4. Preserve the header as company if nothing can be inferred.
        """

        header = header.strip()

        if not header:
            return None, None

        # ---------------------------------------------------------
        # 1. Connecteur explicite
        #
        # Data Engineer chez Liora
        # Developer at ACME
        # ---------------------------------------------------------

        connector_match = cls.ROLE_COMPANY_CONNECTOR_PATTERN.search(
            header
        )

        if connector_match:
            role = header[: connector_match.start()].strip()
            company = header[connector_match.end():].strip()

            if role and company:
                return role, company

        # ---------------------------------------------------------
        # 2. Séparateur explicite par virgule
        #
        # Administrative Assistant, Arowwai Industries
        # Office Coordinator, Borcelle
        # Internship, Salford & Co Corporation
        # ---------------------------------------------------------

        if "," in header:

            role_part, company_part = header.split(
                ",",
                maxsplit=1,
            )

            role_part = role_part.strip()
            company_part = company_part.strip()

            if role_part and company_part:
                return role_part, company_part

        # ---------------------------------------------------------
        # 2. Header multi-lignes
        #
        # Borcelle Studio
        # Marketing Manager & Specialist
        #
        # ACME France
        # Chef de projet Data
        # ---------------------------------------------------------

        lines = cls._split_header_lines(header)

        if len(lines) >= 2:

            role_candidates = [
                line
                for line in lines
                if cls._looks_like_job_title(line)
            ]

            # Cas non ambigu :
            # exactement une ligne ressemble à un métier.
            if len(role_candidates) == 1:
                role = role_candidates[0]

                company_lines = [
                    line
                    for line in lines
                    if line != role
                ]

                company = " ".join(
                    company_lines
                ).strip()

                if company:
                    return role, company

        # ---------------------------------------------------------
        # 3. Rôles connus
        #
        # Utile pour les headers sur une seule ligne :
        #
        # IA & Machine Learning Engineer Liora
        #
        # Adiict | Findeur | Cotep Développeur Informatique
        # ---------------------------------------------------------

        header_lower = header.lower()

        roles = sorted(
            cls.KNOWN_ROLES,
            key=len,
            reverse=True,
        )

        for role in roles:

            role_lower = role.lower()

            index = header_lower.find(role_lower)

            if index == -1:
                continue

            company_before = (
                header[:index]
                .strip()
            )

            company_after = (
                header[index + len(role):]
                .strip()
            )

            company_parts = [
                part
                for part in (
                    company_before,
                    company_after,
                )
                if part
            ]

            company = " ".join(
                company_parts
            ).strip()

            return role, company or None

        # ---------------------------------------------------------
        # 4. Heuristique générique pour les headers mono-ligne
        #
        # Exemples :
        #
        # Cloud Architect ACME Cloud
        # ACME Cloud Cloud Architect
        # Product Owner FinTech Corp
        # DataVision Analyste BI
        # ---------------------------------------------------------

        role, company = cls._split_single_line_role_company(
            header
        )

        if role and company:
            return role, company

        # ---------------------------------------------------------
        # 4. Aucun indice exploitable
        # ---------------------------------------------------------

        return None, header

    @classmethod
    def _looks_like_job_title(cls, text: str) -> bool:
        """Heuristic: does this text look like a job title?"""

        text_lower = text.lower()

        return any(
            keyword in text_lower
            for keyword in cls.JOB_TITLE_KEYWORDS
        )

    @staticmethod
    def _split_header_lines(
        text: str,
    ) -> list[str]:
        """Split a block into non-empty lines."""

        return [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    @staticmethod
    def _normalize_description_block(
            text: str,
    ) -> list[str]:
        """
        Reconstruct logical description items from PDF line wrapping.

        A line break may represent either:

        - a visual wrapping artefact:
            "Develop marketing strategies and"
            "campaigns for customers."

        - a real sentence boundary:
            "First task."
            "Second task."

        Lines are therefore merged until a sentence-ending
        punctuation mark is encountered.
        """

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return []

        items: list[str] = []
        current_parts: list[str] = []

        for line in lines:

            current_parts.append(line)

            # Une phrase est considérée terminée lorsqu'elle
            # se termine par une ponctuation forte.
            if ExperienceExtractor._ends_logical_item(line):

                item = " ".join(current_parts).strip()

                if item:
                    items.append(item)

                current_parts = []

        # Il peut rester un fragment sans ponctuation finale.
        if current_parts:
            item = " ".join(current_parts).strip()

            if item:
                items.append(item)

        return items

    @staticmethod
    def _ends_logical_item(
            text: str,
    ) -> bool:
        """Return True when a line appears to end a logical sentence."""

        text = text.rstrip()

        if not text:
            return False

        return text.endswith(
            (
                ".",
                "!",
                "?",
                ";",
            )
        )

    @classmethod
    def _split_single_line_role_company(
            cls,
            text: str,
    ) -> tuple[str | None, str | None]:
        """Try to split a single-line role/company header generically."""

        words = text.split()

        if len(words) < 2:
            return None, None

        # ---------------------------------------------------------
        # 1. Rôle avant entreprise
        #
        # Cloud Architect ACME Cloud
        # Product Owner FinTech Corp
        #
        # On prend le PREMIER préfixe qui ressemble clairement
        # à un intitulé de poste.
        # ---------------------------------------------------------

        for end in range(1, len(words)):
            role_candidate = " ".join(
                words[:end]
            )

            if not cls._looks_like_job_title(
                    role_candidate
            ):
                continue

            company_candidate = " ".join(
                words[end:]
            ).strip()

            if company_candidate:
                return role_candidate, company_candidate

        # ---------------------------------------------------------
        # 2. Entreprise avant rôle
        #
        # DataVision Analyste BI
        # ACME Cloud Cloud Architect
        #
        # Ici on cherche le meilleur suffixe métier.
        # ---------------------------------------------------------

        candidates: list[
            tuple[int, int, str, str]
        ] = []

        for start in range(1, len(words)):
            company_candidate = " ".join(
                words[:start]
            ).strip()

            role_candidate = " ".join(
                words[start:]
            )

            if not company_candidate:
                continue

            if not cls._looks_like_job_title(
                    role_candidate
            ):
                continue

            score = cls._score_job_title(
                role_candidate
            )

            candidates.append(
                (
                    score,
                    len(role_candidate.split()),
                    role_candidate,
                    company_candidate,
                )
            )

        if not candidates:
            return None, None

        best = max(
            candidates,
            key=lambda candidate: (
                candidate[0],
                candidate[1],
            ),
        )

        _, _, role, company = best

        return role, company

    @classmethod
    def _score_job_title(
        cls,
        text: str,
    ) -> int:
        """Score how strongly a piece of text looks like a job title."""

        normalized = text.lower().strip()

        score = 0

        for keyword in cls.JOB_TITLE_KEYWORDS:
            keyword = keyword.lower()

            if normalized == keyword:
                score = max(score, 5)

            elif normalized.startswith(
                keyword + " "
            ):
                score = max(score, 4)

            elif normalized.endswith(
                " " + keyword
            ):
                score = max(score, 3)

            elif keyword in normalized:
                score = max(score, 1)

        return score
import re

from app.models.cv import Experience
from app.services.layout_extractor import TextBlock


class ExperienceExtractor:
    """Extract professional experiences from PDF text blocks."""

    DATE_RANGE_PATTERN = re.compile(
        r"\(?\s*"
        r"(\d{4})"
        r"\s*[-–—]\s*"
        r"(\d{4}|présent|present|aujourd'hui)"
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
        "Data Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Développeur Full-Stack",
        "Développeur Full Stack",
        "Développeur Web",
        "Ingénieur Logiciel",
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
            match = self.DATE_RANGE_PATTERN.search(block.text)

            if match:
                start_date = match.group(1)
                end_date = match.group(2)
                date_block_index = index
                break

        # ---------------------------------------------------------
        # 2. Construire les blocs d'en-tête
        #
        # Exemple :
        #
        # Airweb - Paragon ID
        # Développeur Back-end
        # (2021 - 2025)
        #
        # => header = "Airweb - Paragon ID Développeur Back-end"
        # ---------------------------------------------------------

        if date_block_index is not None:
            header_blocks = blocks[: date_block_index + 1]
        else:
            header_blocks = blocks[:1]

        header = " ".join(
            block.text.strip()
            for block in header_blocks
            if block.text.strip()
        )

        # ---------------------------------------------------------
        # 3. Supprimer les dates de l'en-tête
        # ---------------------------------------------------------

        header_without_date = (
            self.DATE_RANGE_PATTERN
            .sub("", header)
            .strip()
        )

        # ---------------------------------------------------------
        # 4. Extraire rôle + entreprise
        # ---------------------------------------------------------

        role, company = self._extract_role_company(
            header_without_date
        )

        # ---------------------------------------------------------
        # 5. Description
        #
        # Tout ce qui vient après le bloc contenant les dates
        # est considéré comme description.
        # ---------------------------------------------------------

        description: list[str] = []

        if date_block_index is not None:
            description_blocks = blocks[date_block_index + 1 :]
        else:
            description_blocks = blocks[1:]

        for block in description_blocks:
            for line in block.text.splitlines():
                line = line.strip()

                if line:
                    description.append(line)

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

        1. Un connecteur explicite ("chez", "at"...) sépare
           clairement le rôle (avant) de l'entreprise (après).
           Ce cas généralise à n'importe quel intitulé.
        2. Sinon, on cherche un rôle connu (KNOWN_ROLES) dans le
           texte, comme avant : c'est nécessaire car les en-têtes
           réels sont trop ambigus (séparateurs utilisés pour
           joindre plusieurs entreprises, absence totale de
           séparateur...) pour être résolus sans connaître le rôle.
        3. À défaut, on garde le texte comme entreprise potentielle
           plutôt que de tout perdre.
        """

        header = header.strip()

        if not header:
            return None, None

        connector_match = cls.ROLE_COMPANY_CONNECTOR_PATTERN.search(
            header
        )

        if connector_match:
            role = header[: connector_match.start()].strip()
            company = header[connector_match.end():].strip()

            if role and company:
                return role, company

        header_lower = header.lower()

        # Rôles connus, triés par longueur décroissante pour éviter
        # qu'un rôle court soit trouvé avant un rôle plus spécifique.
        roles = sorted(cls.KNOWN_ROLES, key=len, reverse=True)

        for role in roles:
            role_lower = role.lower()

            index = header_lower.find(role_lower)

            if index == -1:
                continue

            company_before = header[:index].strip()
            company_after = header[index + len(role):].strip()

            company_parts = [
                part
                for part in (company_before, company_after)
                if part
            ]

            company = " ".join(company_parts).strip()

            return role, company or None

        # ---------------------------------------------------------
        # Repli : aucun indice trouvé, on garde le texte comme
        # entreprise potentielle plutôt que de tout perdre.
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
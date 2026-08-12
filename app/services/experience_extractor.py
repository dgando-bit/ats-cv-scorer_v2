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
        """Extract role and company from an experience header."""

        header = header.strip()

        if not header:
            return None, None

        header_lower = header.lower()

        # ---------------------------------------------------------
        # Chercher un rôle connu.
        #
        # On trie par longueur décroissante afin d'éviter qu'un
        # rôle court soit trouvé avant un rôle plus spécifique.
        # ---------------------------------------------------------

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

            company_before = header[:index].strip()
            company_after = header[
                index + len(role) :
            ].strip()

            # Le nom de l'entreprise peut être avant ou après
            # le rôle.
            company_parts = [
                part
                for part in (
                    company_before,
                    company_after,
                )
                if part
            ]

            company = " ".join(company_parts).strip()

            return role, company or None

        # ---------------------------------------------------------
        # Aucun rôle connu.
        #
        # On garde le texte comme entreprise potentielle.
        # ---------------------------------------------------------

        return None, header

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
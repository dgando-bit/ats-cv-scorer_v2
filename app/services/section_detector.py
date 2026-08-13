from dataclasses import dataclass

from app.services.layout_extractor import TextBlock


@dataclass
class DetectedSection:
    name: str
    blocks: list[TextBlock]


class SectionDetector:

    SECTION_ALIASES = {
        "profile": {
            "profil",
            "profile",
            "summary",
            "professional summary",
            "about me",
            "à propos",
        },
        "experience": {
            "expériences",
            "experiences",
            "experience",
            "work experience",
            "professional experience",
        },
        "skills": {
            "compétences",
            "competences",
            "compétences clés",
            "skills",
            "technical skills",
            "core skills",
        },
        "education": {
            "formation",
            "formations",
            "education",
            "academic background",
        },
        "languages": {
            "langues",
            "languages",
        },
        "contact": {
            "contact",
            "coordonnées",
            "contact information",
        },
        "soft_skills": {
            "soft-skills",
            "soft skills",
            "qualités",
            "personal skills",
        },
        "tools": {
            "outils",
            "tools",
            "technologies",
        },
        "references": {
            "reference",
            "references",
            "référence",
            "références",
        },
    }

    def detect(
        self,
        blocks: list[TextBlock],
    ) -> list[DetectedSection]:

        if not blocks:
            return []

        # Pour l'instant, on traite chaque colonne séparément.
        columns = self._split_columns(blocks)

        sections: list[DetectedSection] = []

        for column_blocks in columns:

            column_sections = self._detect_column(
                column_blocks
            )

            sections.extend(column_sections)

        return sections

    def _detect_column(
        self,
        blocks: list[TextBlock],
    ) -> list[DetectedSection]:

        sections: list[DetectedSection] = []

        current_section: str | None = None
        current_blocks: list[TextBlock] = []

        # Lecture verticale dans la colonne
        blocks = sorted(
            blocks,
            key=lambda block: block.y0,
        )

        for block in blocks:

            section_name = self._match_section(
                block.text
            )

            if section_name:

                if current_section is not None:
                    sections.append(
                        DetectedSection(
                            name=current_section,
                            blocks=current_blocks,
                        )
                    )

                current_section = section_name
                current_blocks = []

                continue

            if current_section is not None:
                current_blocks.append(block)

        if current_section is not None:
            sections.append(
                DetectedSection(
                    name=current_section,
                    blocks=current_blocks,
                )
            )

        return sections

    @classmethod
    def _split_columns(
        cls,
        blocks: list[TextBlock],
    ) -> list[list[TextBlock]]:
        """Split blocks into columns based on the layout actually
        detected, instead of assuming a fixed pixel threshold.

        Une mise en page mono-colonne renvoie une seule "colonne"
        (tous les blocs). Une mise en page à deux colonnes est
        détectée en cherchant un espace vertical significatif entre
        deux groupes de blocs, proche du centre de la page.
        """

        if not blocks:
            return []

        page_width = blocks[0].page_width

        split_x = cls._find_column_split(blocks, page_width)

        if split_x is None:
            # Pas de séparation nette détectée : on considère
            # que le document est en une seule colonne.
            return [blocks]

        left_column = [
            block for block in blocks if block.x0 < split_x
        ]
        right_column = [
            block for block in blocks if block.x0 >= split_x
        ]

        return [left_column, right_column]

    @staticmethod
    def _find_column_split(
        blocks: list[TextBlock],
        page_width: float,
        min_gap_ratio: float = 0.06,
        min_side_ratio: float = 0.15,
    ) -> float | None:
        """Find an x-coordinate that separates two columns of text.

        On trie les positions x0 de TOUS les blocs (avec doublons,
        pour pondérer par le nombre de blocs) et on cherche le plus
        grand "trou" horizontal.

        Contrairement à une simple recherche du plus grand écart,
        on exige qu'au moins `min_side_ratio` des blocs se trouvent
        de chaque côté du split. Cela évite qu'un petit groupe
        isolé de blocs (ex: une sous-colonne de 2 blocs dans un
        bloc "Compétences" à deux sous-colonnes) ne soit pris à
        tort pour la séparation principale entre la sidebar et le
        contenu principal — un vrai CV à deux colonnes a ses deux
        colonnes peuplées sur presque toute la hauteur de page,
        alors qu'un artefact local ne concerne que quelques blocs.
        """

        if page_width <= 0:
            return None

        xs = sorted(block.x0 for block in blocks)

        total = len(xs)

        if total < 2:
            return None

        min_gap = page_width * min_gap_ratio
        min_side_count = max(3, round(total * min_side_ratio))

        best_gap = 0.0
        best_split: float | None = None

        for index in range(1, total):

            left_count = index
            right_count = total - index

            if (
                left_count < min_side_count
                or right_count < min_side_count
            ):
                continue

            gap = xs[index] - xs[index - 1]

            if gap > best_gap:
                best_gap = gap
                best_split = (
                    xs[index - 1] + xs[index]
                ) / 2

        if best_gap >= min_gap:
            return best_split

        return None

    def _match_section(
        self,
        text: str,
    ) -> str | None:

        normalized = self._normalize(text)

        for section_name, aliases in self.SECTION_ALIASES.items():

            if normalized in aliases:
                return section_name

        return None

    @staticmethod
    def _normalize(text: str) -> str:

        return (
            text.strip()
            .lower()
            .replace(":", "")
        )
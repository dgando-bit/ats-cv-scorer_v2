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
            "career history",
        },
        "skills": {
            "compétences",
            "competences",
            "compétences clés",
            "skills",
            "technical skills",
            "core skills",
            "core competencies",
            "key skills",
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
            "language",
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
            "tech stack",
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

        # ---------------------------------------------------------
        # 1. Sections parallèles
        # ---------------------------------------------------------

        parallel_sections, remaining_blocks = (
            self._extract_parallel_sections(blocks)
        )

        # ---------------------------------------------------------
        # 2. Sections qui s'étendent sur plusieurs colonnes locales
        # ---------------------------------------------------------

        spanning_sections, remaining_blocks = (
            self._extract_spanning_education(
                remaining_blocks
            )
        )

        # ---------------------------------------------------------
        # 3. Découpage global classique
        # ---------------------------------------------------------

        columns = self._split_columns(
            remaining_blocks
        )

        sections: list[DetectedSection] = []

        for column_blocks in columns:
            sections.extend(
                self._detect_column(
                    column_blocks
                )
            )

        sections.extend(spanning_sections)
        sections.extend(parallel_sections)

        return sections

    def _detect_column(
            self,
            blocks: list[TextBlock],
    ) -> list[DetectedSection]:

        sections: list[DetectedSection] = []

        current_section: str | None = None
        current_blocks: list[TextBlock] = []

        # Cas spécial pour plusieurs sections parallèles :
        #
        # KEY SKILLS        LANGUAGE
        # skill ...         English ...
        #
        parallel_sections: list[str] | None = None
        parallel_blocks: list[TextBlock] = []

        blocks = sorted(
            blocks,
            key=lambda block: block.y0,
        )

        for block in blocks:

            section_names = self._match_sections(
                block.text
            )

            if section_names:

                # -----------------------------------------------------
                # Terminer d'éventuelles sections parallèles
                # -----------------------------------------------------

                if parallel_sections is not None:
                    sections.extend(
                        self._build_parallel_sections(
                            parallel_sections,
                            parallel_blocks,
                        )
                    )

                    parallel_sections = None
                    parallel_blocks = []

                # -----------------------------------------------------
                # Terminer la section verticale courante
                # -----------------------------------------------------

                if current_section is not None:
                    sections.append(
                        DetectedSection(
                            name=current_section,
                            blocks=current_blocks,
                        )
                    )

                    current_section = None
                    current_blocks = []

                # -----------------------------------------------------
                # Cas simple : un seul heading
                # -----------------------------------------------------

                if len(section_names) == 1:
                    current_section = section_names[0]
                    continue

                # -----------------------------------------------------
                # Cas :
                #
                # KEY SKILLS
                # LANGUAGE
                #
                # On mémorise les sections et on collectera les blocs
                # suivants avant de les répartir horizontalement.
                # -----------------------------------------------------

                parallel_sections = section_names
                parallel_blocks = []

                continue

            # ---------------------------------------------------------
            # Contenu de sections parallèles
            # ---------------------------------------------------------

            if parallel_sections is not None:
                parallel_blocks.append(block)
                continue

            # ---------------------------------------------------------
            # Contenu d'une section verticale classique
            # ---------------------------------------------------------

            if current_section is not None:
                current_blocks.append(block)

        # -------------------------------------------------------------
        # Fin du document / de la colonne
        # -------------------------------------------------------------

        if parallel_sections is not None:
            sections.extend(
                self._build_parallel_sections(
                    parallel_sections,
                    parallel_blocks,
                )
            )

        if current_section is not None:
            sections.append(
                DetectedSection(
                    name=current_section,
                    blocks=current_blocks,
                )
            )

        return sections

    @staticmethod
    def _build_parallel_sections(
            section_names: list[str],
            blocks: list[TextBlock],
    ) -> list[DetectedSection]:
        """Distribute blocks between parallel sections."""

        if not section_names:
            return []

        if not blocks:
            return [
                DetectedSection(
                    name=name,
                    blocks=[],
                )
                for name in section_names
            ]

        if len(section_names) == 1:
            return [
                DetectedSection(
                    name=section_names[0],
                    blocks=sorted(
                        blocks,
                        key=lambda block: block.y0,
                    ),
                )
            ]

        # ---------------------------------------------------------
        # 1. Regrouper les blocs en colonnes horizontales locales.
        # ---------------------------------------------------------

        sorted_blocks = sorted(
            blocks,
            key=lambda block: block.x0,
        )

        local_groups: list[list[TextBlock]] = []

        current_group: list[TextBlock] = [
            sorted_blocks[0]
        ]

        # Deux blocs dont les x0 sont suffisamment proches
        # appartiennent à la même sous-colonne.
        x_gap_threshold = 80

        for block in sorted_blocks[1:]:

            previous = current_group[-1]

            if block.x0 - previous.x0 < x_gap_threshold:
                current_group.append(block)
            else:
                local_groups.append(current_group)
                current_group = [block]

        local_groups.append(current_group)

        # ---------------------------------------------------------
        # 2. S'il y a autant de groupes que de sections :
        #
        # groupe 1 -> section 1
        # groupe 2 -> section 2
        # ---------------------------------------------------------

        if len(local_groups) == len(section_names):
            return [
                DetectedSection(
                    name=section_name,
                    blocks=sorted(
                        group,
                        key=lambda block: block.y0,
                    ),
                )
                for section_name, group in zip(
                    section_names,
                    local_groups,
                )
            ]

        # ---------------------------------------------------------
        # 3. Plus de colonnes que de sections.
        #
        # Exemple réel :
        #
        # skills       skills        languages
        # x=53         x=234         x=414
        #
        # avec seulement :
        #
        # KEY SKILLS | LANGUAGE
        #
        # On affecte le dernier groupe à la dernière section,
        # et les groupes précédents à la première section.
        # ---------------------------------------------------------

        if (
                len(section_names) == 2
                and len(local_groups) > 2
        ):
            first_section_blocks = [
                block
                for group in local_groups[:-1]
                for block in group
            ]

            second_section_blocks = (
                local_groups[-1]
            )

            return [
                DetectedSection(
                    name=section_names[0],
                    blocks=sorted(
                        first_section_blocks,
                        key=lambda block: (
                            block.y0,
                            block.x0,
                        ),
                    ),
                ),
                DetectedSection(
                    name=section_names[1],
                    blocks=sorted(
                        second_section_blocks,
                        key=lambda block: (
                            block.y0,
                            block.x0,
                        ),
                    ),
                ),
            ]

        # ---------------------------------------------------------
        # 4. Fallback.
        # ---------------------------------------------------------

        detected_sections: list[DetectedSection] = []

        for index, section_name in enumerate(
                section_names
        ):
            group = (
                local_groups[index]
                if index < len(local_groups)
                else []
            )

            detected_sections.append(
                DetectedSection(
                    name=section_name,
                    blocks=sorted(
                        group,
                        key=lambda block: block.y0,
                    ),
                )
            )

        return detected_sections

    def _extract_spanning_education(
            self,
            blocks: list[TextBlock],
    ) -> tuple[list[DetectedSection], list[TextBlock]]:
        """
        Extract an education section that spans several local columns.

        Example:

            EDUCATION

            Jan 2019 ...             Jan 2018 ...
            University A            University B
        """

        sorted_blocks = sorted(
            blocks,
            key=lambda block: (
                block.page,
                block.y0,
            ),
        )

        for heading_block in sorted_blocks:

            section_names = self._match_sections(
                heading_block.text
            )

            if section_names != ["education"]:
                continue

            # -----------------------------------------------------
            # Si un autre heading existe horizontalement au même
            # niveau, EDUCATION appartient probablement à une
            # colonne distincte et ne doit pas s'étendre sur toute
            # la page.
            #
            # Exemple :
            #
            # EDUCATION              EXPERIENCE
            # -----------------------------------------------------

            has_parallel_heading = any(
                candidate is not heading_block
                and candidate.page == heading_block.page
                and abs(candidate.y0 - heading_block.y0) <= 30
                and bool(self._match_sections(candidate.text))
                for candidate in sorted_blocks
            )

            if has_parallel_heading:
                continue

            # -----------------------------------------------------
            # Trouver le prochain heading plus bas sur la même page.
            # Il marque la fin de la zone EDUCATION.
            # -----------------------------------------------------

            next_heading_y: float | None = None

            for candidate in sorted_blocks:

                if candidate.page != heading_block.page:
                    continue

                if candidate.y0 <= heading_block.y0:
                    continue

                candidate_sections = self._match_sections(
                    candidate.text
                )

                if candidate_sections:
                    next_heading_y = candidate.y0
                    break

            # -----------------------------------------------------
            # Récupérer tous les blocs sous EDUCATION,
            # indépendamment de leur x0.
            # -----------------------------------------------------

            education_blocks: list[TextBlock] = []

            for candidate in sorted_blocks:

                if candidate is heading_block:
                    continue

                if candidate.page != heading_block.page:
                    continue

                if candidate.y0 <= heading_block.y1:
                    continue

                if (
                        next_heading_y is not None
                        and candidate.y0 >= next_heading_y
                ):
                    continue

                education_blocks.append(candidate)

            if not education_blocks:
                continue

            # -----------------------------------------------------
            # Important :
            # on ne considère la section comme "spanning" que si
            # son contenu occupe réellement plusieurs zones
            # horizontales.
            # -----------------------------------------------------

            xs = sorted(
                block.x0
                for block in education_blocks
            )

            if len(xs) < 2:
                continue

            max_gap = max(
                xs[index] - xs[index - 1]
                for index in range(1, len(xs))
            )

            # Pas de séparation horizontale significative :
            # on laisse le traitement classique faire.
            if max_gap < 80:
                continue

            # -----------------------------------------------------
            # Vérifier qu'il s'agit réellement de deux sous-colonnes
            # appartenant à la même section EDUCATION.
            #
            # Une section parallèle commence normalement à une
            # hauteur similaire dans les deux colonnes.
            # -----------------------------------------------------

            sorted_by_x = sorted(
                education_blocks,
                key=lambda block: block.x0,
            )

            # Trouver la séparation horizontale principale.
            best_gap = 0.0
            split_index: int | None = None

            for index in range(1, len(sorted_by_x)):

                gap = (
                        sorted_by_x[index].x0
                        - sorted_by_x[index - 1].x0
                )

                if gap > best_gap:
                    best_gap = gap
                    split_index = index

            if split_index is None:
                continue

            left_group = sorted_by_x[:split_index]
            right_group = sorted_by_x[split_index:]

            if not left_group or not right_group:
                continue

            left_start_y = min(
                block.y0
                for block in left_group
            )

            right_start_y = min(
                block.y0
                for block in right_group
            )

            # Les deux colonnes doivent commencer presque
            # à la même hauteur.
            if abs(left_start_y - right_start_y) > 30:
                continue

            consumed_ids = {
                id(heading_block),
                *(
                    id(block)
                    for block in education_blocks
                ),
            }

            remaining_blocks = [
                block
                for block in blocks
                if id(block) not in consumed_ids
            ]

            education_blocks = sorted(
                education_blocks,
                key=lambda block: (
                    0
                    if block.x0 < heading_block.page_width / 2
                    else 1,
                    block.y0,
                ),
            )

            return (
                [
                    DetectedSection(
                        name="education",
                        blocks=education_blocks,
                    )
                ],
                remaining_blocks,
            )

        return [], blocks

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

    def _match_sections(
            self,
            text: str,
    ) -> list[str]:

        section_names: list[str] = []

        for line in text.splitlines():
            normalized = self._normalize(line)

            for section_name, aliases in self.SECTION_ALIASES.items():
                if normalized in aliases:
                    section_names.append(section_name)
                    break

        return section_names

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

    def _extract_parallel_sections(
            self,
            blocks: list[TextBlock],
    ) -> tuple[list[DetectedSection], list[TextBlock]]:
        """Extract local zones containing multiple section headings."""

        parallel_sections: list[DetectedSection] = []

        consumed_ids: set[int] = set()

        # Ordre vertical
        sorted_blocks = sorted(
            blocks,
            key=lambda block: (
                block.page,
                block.y0,
            ),
        )

        for heading_block in sorted_blocks:

            section_names = self._match_sections(
                heading_block.text
            )

            # On ne s'intéresse ici qu'aux blocs contenant
            # plusieurs headings.
            if len(section_names) < 2:
                continue

            consumed_ids.add(
                id(heading_block)
            )

            # -----------------------------------------------------
            # Chercher la prochaine section située plus bas.
            # Elle marque la fin de la zone parallèle.
            # -----------------------------------------------------

            next_heading_y: float | None = None

            for candidate in sorted_blocks:

                if candidate.page != heading_block.page:
                    continue

                if candidate.y0 <= heading_block.y0:
                    continue

                candidate_sections = self._match_sections(
                    candidate.text
                )

                if candidate_sections:
                    next_heading_y = candidate.y0
                    break

            # -----------------------------------------------------
            # Récupérer TOUS les blocs de la zone, quelle que soit
            # leur position horizontale.
            # -----------------------------------------------------

            zone_blocks: list[TextBlock] = []

            for candidate in sorted_blocks:

                if candidate.page != heading_block.page:
                    continue

                if candidate.y0 <= heading_block.y1:
                    continue

                if (
                        next_heading_y is not None
                        and candidate.y0 >= next_heading_y
                ):
                    continue

                zone_blocks.append(candidate)
                consumed_ids.add(
                    id(candidate)
                )

            parallel_sections.extend(
                self._build_parallel_sections(
                    section_names,
                    zone_blocks,
                )
            )

        # ---------------------------------------------------------
        # Retirer du traitement classique les blocs déjà consommés.
        # ---------------------------------------------------------

        remaining_blocks = [
            block
            for block in blocks
            if id(block) not in consumed_ids
        ]

        return parallel_sections, remaining_blocks
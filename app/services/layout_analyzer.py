from dataclasses import dataclass

from app.services.layout_extractor import TextBlock


@dataclass
class LayoutColumn:
    name: str
    blocks: list[TextBlock]


class LayoutAnalyzer:
    """
    Analyze the spatial organization of PDF text blocks.
    """

    def analyze(
        self,
        blocks: list[TextBlock],
    ) -> dict[str, LayoutColumn]:

        if not blocks:
            return {}

        x_positions = sorted(
            block.center_x
            for block in blocks
        )

        split_position = self._find_column_split(x_positions)

        sidebar = []
        main = []

        for block in blocks:
            if block.center_x < split_position:
                sidebar.append(block)
            else:
                main.append(block)

        sidebar.sort(key=lambda block: block.y0)
        main.sort(key=lambda block: block.y0)

        return {
            "sidebar": LayoutColumn(
                name="sidebar",
                blocks=sidebar,
            ),
            "main": LayoutColumn(
                name="main",
                blocks=main,
            ),
        }

    @staticmethod
    def _find_column_split(
        x_positions: list[float],
    ) -> float:

        if len(x_positions) < 2:
            return x_positions[0]

        largest_gap = 0
        split_position = x_positions[0]

        for left, right in zip(
            x_positions,
            x_positions[1:],
        ):
            gap = right - left

            if gap > largest_gap:
                largest_gap = gap
                split_position = (left + right) / 2

        return split_position
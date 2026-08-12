from dataclasses import dataclass

import pymupdf


@dataclass
class TextBlock:
    page: int
    page_width: float
    x0: float
    y0: float
    x1: float
    y1: float
    text: str

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2


class LayoutExtractor:
    """Extract PDF text blocks while preserving their spatial coordinates."""

    def extract(self, file_path: str) -> list[TextBlock]:
        blocks: list[TextBlock] = []

        with pymupdf.open(file_path) as document:
            for page_number, page in enumerate(document, start=1):
                for block in page.get_text("blocks"):
                    x0, y0, x1, y1, text, *_ = block

                    text = self._clean_text(text)

                    if not text:
                        continue

                    blocks.append(
                        TextBlock(
                            page=page_number,
                            page_width=page.rect.width,
                            x0=x0,
                            y0=y0,
                            x1=x1,
                            y1=y1,
                            text=text,
                        )
                    )

        return blocks

    @staticmethod
    def _clean_text(text: str) -> str:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)
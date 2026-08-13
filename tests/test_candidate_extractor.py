from app.services.cv_extractor import CVExtractor
from app.services.layout_extractor import TextBlock


def make_block(
    text: str,
    x: float,
    y: float,
) -> TextBlock:
    return TextBlock(
        page=1,
        page_width=595,
        x0=x,
        y0=y,
        x1=x + 250,
        y1=y + 20,
        text=text,
    )


def test_extract_candidate_name_not_first_block():
    blocks = [
        make_block("EDUCATION", 30, 40),
        make_block("RICHARD SANCHEZ", 230, 20),
        make_block("MARKETING MANAGER", 230, 55),
    ]

    name = CVExtractor._extract_candidate_name(blocks)

    assert name == "RICHARD SANCHEZ"


def test_extract_candidate_title_below_name():
    blocks = [
        make_block("EDUCATION", 30, 40),
        make_block("RICHARD SANCHEZ", 230, 20),
        make_block("MARKETING MANAGER", 230, 55),
    ]

    title = CVExtractor._extract_title(blocks)

    assert title == "MARKETING MANAGER"
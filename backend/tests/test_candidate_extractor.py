from app.services.cv.cv_extractor import CVExtractor
from app.services.cv.layout_extractor import TextBlock


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

def test_extract_candidate_title_ignores_profile_paragraph():
    blocks = [
        make_block(
            "RICHARD SANCHEZ",
            230,
            20,
        ),
        make_block(
            "MARKETING MANAGER",
            230,
            50,
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=230,
            y0=90,
            x1=550,
            y1=180,
            text=(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit,\n"
                "sed do eiusmod tempor incididunt ut labore et dolore."
            ),
        ),
    ]

    title = CVExtractor._extract_title(blocks)

    assert title == "MARKETING MANAGER"
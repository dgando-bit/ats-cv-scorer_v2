from app.services.cv_extractor import CVExtractor
from app.services.layout_extractor import TextBlock

def test_website_is_not_location():
    text = """
    hello@reallygreatsite.com
    www.reallygreatsite.com
    """

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.email == "hello@reallygreatsite.com"
    assert contact.website == "www.reallygreatsite.com"
    assert contact.location is None


def test_extract_location_and_website_separately():
    text = """
    Paris, France
    www.example.com
    """

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.location == "Paris, France"
    assert contact.website == "www.example.com"


def test_extract_complete_contact():
    text = """
    +33 6 12 34 56 78
    john.doe@example.com
    Paris, France
    www.johndoe.dev
    """

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.phone == "+33 6 12 34 56 78"
    assert contact.email == "john.doe@example.com"
    assert contact.location == "Paris, France"
    assert contact.website == "www.johndoe.dev"

def test_extract_contact_from_single_line():
    text = (
        "hello@reallygreatsite.com | "
        "123-456-7890 | "
        "123 Anywhere St., Any City"
    )

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.email == "hello@reallygreatsite.com"
    assert contact.phone == "123-456-7890"
    assert contact.location == "123 Anywhere St., Any City"

def test_top_contact_text_ignores_candidate_name_and_title():

    blocks = [
        TextBlock(
            page=1,
            page_width=595,
            x0=230,
            y0=60,
            x1=470,
            y1=100,
            text="DANI MARTINEZ",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=230,
            y0=101,
            x1=390,
            y1=120,
            text="Administrative Manager",
        ),
        TextBlock(
            page=1,
            page_width=595,
            x0=230,
            y0=127,
            x1=570,
            y1=156,
            text=(
                "hello@reallygreatsite.com | "
                "123-456-7890 | "
                "123 Anywhere St., Any City"
            ),
        ),
    ]

    extractor = CVExtractor()

    text = extractor._extract_top_contact_text(
        blocks
    )

    assert "DANI MARTINEZ" not in text
    assert "Administrative Manager" not in text

    assert "hello@reallygreatsite.com" in text
    assert "123-456-7890" in text
    assert "123 Anywhere St., Any City" in text

def test_extract_wrapped_address():
    text = (
        "hello@reallygreatsite.com | "
        "123-456-7890 | 123\n"
        "Anywhere St., Any City"
    )

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.email == "hello@reallygreatsite.com"
    assert contact.phone == "123-456-7890"
    assert contact.location == "123 Anywhere St., Any City"

def test_phone_with_plus_is_not_location():
    text = """
    +123-456-7890
    hello@reallygreatsite.com
    123 Anywhere St., Any City
    www.reallygreatsite.com
    """

    extractor = CVExtractor()

    contact = extractor._extract_contact(text)

    assert contact.phone == "123-456-7890"
    assert contact.location == "123 Anywhere St., Any City"
    assert contact.website == "www.reallygreatsite.com"
from app.services.cv_extractor import CVExtractor


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
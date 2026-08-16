from app.services.cv.regex_extractor import RegexExtractor


def test_extract_email():

    extractor = RegexExtractor()

    result = extractor.extract(
        "Contact : test@example.com"
    )

    assert result["emails"] == [
        "test@example.com"
    ]


def test_extract_phone():

    extractor = RegexExtractor()

    result = extractor.extract(
        "Téléphone : +33 6 70 50 41 98"
    )

    assert result["phones"] == [
        "+33 6 70 50 41 98"
    ]


def test_extract_multiple_fields():

    extractor = RegexExtractor()

    text = """
    Destin GANDO
    +33 6 70 50 41 98
    d.gbakary@outlook.com
    """

    result = extractor.extract(text)

    assert result["emails"] == [
        "d.gbakary@outlook.com"
    ]

    assert result["phones"] == [
        "+33 6 70 50 41 98"
    ]

def test_extract_us_phone_number():
    text = (
        "hello@reallygreatsite.com | "
        "123-456-7890 | "
        "123 Anywhere St., Any City"
    )

    extractor = RegexExtractor()

    result = extractor.extract(text)

    assert "123-456-7890" in result["phones"]
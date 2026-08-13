from app.services.cv_extractor import CVExtractor


def test_merge_wrapped_list_item_with_parentheses():
    text = """
    Esprit Analytique
    Rigueur
    Travail en équipe (Agile/Data/
    DevOps)
    """

    items = CVExtractor._extract_list_items(text)

    assert items == [
        "Esprit Analytique",
        "Rigueur",
        "Travail en équipe (Agile/Data/DevOps)",
    ]


def test_keep_independent_list_items():
    text = """
    Python
    Pandas
    FastAPI
    Docker
    """

    items = CVExtractor._extract_list_items(text)

    assert items == [
        "Python",
        "Pandas",
        "FastAPI",
        "Docker",
    ]

def test_split_comma_separated_items():
    text = """
    Python, Pandas, Numpy, Scikit-learn
    """

    items = CVExtractor._extract_list_items(text)

    assert items == [
        "Python",
        "Pandas",
        "Numpy",
        "Scikit-learn",
    ]


def test_merge_parentheses_before_splitting():
    text = """
    Travail en équipe (Agile/Data/
    DevOps)
    """

    items = CVExtractor._extract_list_items(text)

    assert items == [
        "Travail en équipe (Agile/Data/DevOps)"
    ]

# ATS-CV-Scorer
## 1.0.0
## Arborescence du projet
```
ats-cv-scorer_v2/
│
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── cv.py
│   │
│   └── services/
│       ├── document_parser.py
│       ├── layout_extractor.py
│       ├── section_extractor.py
│       └── experience_extractor.py
│
├── tests/
│   ├── test_cv_models.py
│   ├── test_document_parser.py
│   └── test_health.py
│
├── scripts/
│
├── data/
│   └── samples/
│
├── pyproject.toml
└── uv.lock
```

## Pipeline
```
PDF / DOCX
    │
    ▼
DocumentParser
    │
    ▼
LayoutExtractor
    │
    ▼
SectionExtractor
    │
    ├── PROFILE
    ├── CONTACT
    ├── EXPERIENCE ─────► ExperienceExtractor
    ├── EDUCATION
    ├── SKILLS
    └── LANGUAGES
             │
             ▼
        CV structured JSON
             │
             ▼
        NER / NLP
             │
             ▼
        ATS Scoring
```
## job-matching assistant
### Parcours utilisateur
```
Upload CV
   ↓
Extraction du profil
   ↓
Recherche d'offres
   ↓
Sélection d'une offre
   ↓
Matching CV ↔ offre
   ↓
Score + compétences manquantes + recommandations
```
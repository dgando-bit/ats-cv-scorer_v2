# ATS-CV-Scorer
## 1.0.0
## Arborescence du projet
```
ats-cv-scorer_v2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analyze.py
│   │   │       ├── cv.py
│   │   │       ├── job.py
│   │   │       └── match.py
│   │   │
│   │   ├── models/
│   │   │   ├── cv.py
│   │   │   ├── job.py
│   │   │   └── match.py
│   │   │
│   │   ├── services/
│   │   │   ├── cv/
│   │   │   │   ├── cv_extractor.py
│   │   │   │   ├── document_parser.py
│   │   │   │   ├── layout_extractor.py
│   │   │   │   ├── section_detector.py
│   │   │   │   ├── regex_extractor.py
│   │   │   │   ├── experience_extractor.py
│   │   │   │   └── education_extractor.py
│   │   │   │
│   │   │   ├── jobs/
│   │   │   │   ├── job_offer_extractor.py
│   │   │   │   └── providers/
│   │   │   │       ├── base.py
│   │   │   │       └── france_travail.py
│   │   │   │
│   │   │   └── matching/
│   │   │       ├── matching_engine.py
│   │   │       └── skill_normalizer.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── data/
│   │   └── samples/
│   ├── scripts/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
│
├── frontend/
│   └── ...
│
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
└── README.md
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

```
                LLM
                 │
           extraction
                 ↓
        données structurées
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
MatchingEngine         Embeddings
déterministe           sémantique
       │                   │
       ▼                   ▼
match_score       relevance_score
```
Le LLM comprend et structure.

Les embeddings mesurent la proximité sémantique.

Notre code calcule les critères objectifs.
from dataclasses import dataclass, field

from app.models.cv import CV
from app.services.matching.skill_normalizer import SkillNormalizer


@dataclass
class CandidateKnowledge:
    terms: list[str] = field(
        default_factory=list
    )


class CandidateKnowledgeExtractor:

    def extract(
        self,
        cv: CV,
    ) -> CandidateKnowledge:

        texts: list[str] = []

        texts.extend(cv.skills)
        texts.extend(cv.tools)

        if cv.profile:
            texts.append(cv.profile)

        if cv.title:
            texts.append(cv.title)

        for experience in cv.experiences:

            if experience.role:
                texts.append(experience.role)

            if experience.company:
                texts.append(experience.company)

            texts.extend(
                experience.description
            )

        found_terms: list[str] = []

        for text in texts:

            found_terms.extend(
                SkillNormalizer.extract_known_terms(
                    text
                )
            )

        return CandidateKnowledge(
            terms=list(
                dict.fromkeys(found_terms)
            )
        )
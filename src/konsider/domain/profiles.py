"""Default user profiles for Sprint 2 scoring."""

from __future__ import annotations

from konsider.domain.models import DefaultProfile


DEFAULT_PROFILES: dict[str, DefaultProfile] = {
    "indian_tech_professional_with_teenage_child": DefaultProfile(
        id="indian_tech_professional_with_teenage_child",
        name="Indian tech professional with teenage child",
        description=(
            "Balances technology career opportunity with safety, education, healthcare, "
            "and family affordability."
        ),
        weights={
            "tech_jobs": 5,
            "female_safety": 5,
            "university_quality": 5,
            "crime_rate": 4,
            "healthcare": 3,
            "cost_of_living": 3,
            "tax_burden": 2,
            "infrastructure": 2,
            "air_quality": 2,
            "finance_jobs": 1,
        },
    ),
    "student_planning_higher_education": DefaultProfile(
        id="student_planning_higher_education",
        name="Student planning higher education",
        description=(
            "Prioritizes university quality, safety, affordability, infrastructure, "
            "and medium-term job prospects."
        ),
        weights={
            "university_quality": 5,
            "crime_rate": 4,
            "female_safety": 4,
            "cost_of_living": 4,
            "infrastructure": 3,
            "tech_jobs": 2,
            "finance_jobs": 2,
            "healthcare": 2,
            "air_quality": 2,
            "tax_burden": 1,
        },
    ),
    "finance_professional": DefaultProfile(
        id="finance_professional",
        name="Finance professional",
        description=(
            "Prioritizes finance opportunity, tax efficiency, infrastructure, safety, "
            "cost of living, and healthcare."
        ),
        weights={
            "finance_jobs": 5,
            "tax_burden": 5,
            "infrastructure": 5,
            "crime_rate": 3,
            "female_safety": 3,
            "cost_of_living": 3,
            "healthcare": 3,
            "tech_jobs": 2,
            "air_quality": 2,
            "university_quality": 1,
        },
    ),
}


def get_default_profile(profile_id: str) -> DefaultProfile:
    """Return a default profile by id."""

    try:
        return DEFAULT_PROFILES[profile_id]
    except KeyError as exc:
        raise KeyError(f"Unknown default profile: {profile_id}") from exc

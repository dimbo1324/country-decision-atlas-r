from pydantic import BaseModel, Field


class OnboardingSection(BaseModel):
    status: str
    severity: str
    required: int | None = None
    actual: int | None = None
    missing: int | None = None
    message: str = ""


class OnboardingFinding(BaseModel):
    code: str
    severity: str
    message: str


class CountryOnboardingResult(BaseModel):
    country_slug: str
    mvp_ready: bool
    sections: dict[str, OnboardingSection] = Field(default_factory=dict)
    findings: list[OnboardingFinding] = Field(default_factory=list)


class AllCountriesOnboardingResult(BaseModel):
    countries: list[CountryOnboardingResult] = Field(default_factory=list)
    all_mvp_ready: bool

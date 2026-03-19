from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from applyr.agents.job.models import (
    ApplicationDraft,
    ApplicationStatus,
    CompensationRange,
    JobFitScore,
    JobListing,
    JobScoreBreakdown,
    JobSearchQuery,
    JobType,
    ResumeProfile,
    WorkMode,
)
from applyr.core.models import SourceRef


@dataclass(frozen=True)
class JobWorkflowResult:
    query: JobSearchQuery
    listings: list[JobListing]
    scored_jobs: list[JobFitScore]
    drafts: list[ApplicationDraft]


def run_job_workflow(
    query: JobSearchQuery,
    resume_profile: ResumeProfile,
    limit: int = 3,
) -> JobWorkflowResult:
    listings = search_jobs(query)
    scored_jobs = rank_jobs(listings, resume_profile)
    top_jobs = scored_jobs[:limit]
    drafts = [draft_application(score.job, resume_profile, score) for score in top_jobs]
    return JobWorkflowResult(
        query=query,
        listings=listings,
        scored_jobs=scored_jobs,
        drafts=drafts,
    )


def search_jobs(query: JobSearchQuery) -> list[JobListing]:
    normalized_keywords = {keyword.lower() for keyword in query.keywords}
    listings = [
        JobListing(
            title="Senior Python AI Engineer",
            company="Northstar Labs",
            url="https://jobs.example.com/northstar/senior-python-ai-engineer",
            location="Toronto, ON",
            work_mode=WorkMode.HYBRID,
            job_type=JobType.FULL_TIME,
            compensation=CompensationRange(currency="CAD", min_amount=150000, max_amount=185000),
            description="Build agentic systems, LLM workflows, and backend APIs for enterprise products.",
            requirements=["Python", "LLMs", "APIs", "Production systems"],
            responsibilities=["Build AI agents", "Own backend services", "Ship experimentation systems"],
            source=SourceRef(name="SeedBoard", url="https://jobs.example.com"),
        ),
        JobListing(
            title="Remote Applied AI Engineer",
            company="SignalForge",
            url="https://jobs.example.com/signalforge/applied-ai-engineer",
            location="Remote - Canada",
            work_mode=WorkMode.REMOTE,
            job_type=JobType.FULL_TIME,
            compensation=CompensationRange(currency="CAD", min_amount=140000, max_amount=170000),
            description="Design internal copilots, ranking systems, and evaluation pipelines for AI features.",
            requirements=["Python", "Evaluation", "Prompting", "Data pipelines"],
            responsibilities=["Prototype AI workflows", "Measure quality", "Work with product teams"],
            source=SourceRef(name="SeedBoard", url="https://jobs.example.com"),
        ),
        JobListing(
            title="Software Engineer, Platform",
            company="Maple Stack",
            url="https://jobs.example.com/maplestack/platform-engineer",
            location="Toronto, ON",
            work_mode=WorkMode.ONSITE,
            job_type=JobType.FULL_TIME,
            compensation=CompensationRange(currency="CAD", min_amount=120000, max_amount=145000),
            description="Own platform APIs and observability tooling for a fast-growing engineering team.",
            requirements=["Python", "Kubernetes", "Observability"],
            responsibilities=["Maintain APIs", "Improve reliability", "Support developer tooling"],
            source=SourceRef(name="SeedBoard", url="https://jobs.example.com"),
        ),
        JobListing(
            title="AI Solutions Consultant",
            company="BrightPeak",
            url="https://jobs.example.com/brightpeak/ai-solutions-consultant",
            location="Remote - US/Canada",
            work_mode=WorkMode.REMOTE,
            job_type=JobType.CONTRACT,
            compensation=CompensationRange(currency="USD", min_amount=75, max_amount=110, period="hourly"),
            description="Scope AI automation projects for clients and deliver pilot solutions quickly.",
            requirements=["Python", "Client communication", "Automation"],
            responsibilities=["Run discovery", "Build proofs of concept", "Present recommendations"],
            source=SourceRef(name="SeedBoard", url="https://jobs.example.com"),
        ),
    ]

    def matches(job: JobListing) -> bool:
        haystack = " ".join(
            filter(
                None,
                [
                    job.title,
                    job.company,
                    job.location,
                    job.description,
                    " ".join(job.requirements),
                    " ".join(job.responsibilities),
                ],
            )
        ).lower()
        if normalized_keywords and not any(keyword in haystack for keyword in normalized_keywords):
            return False
        if query.location and query.location.lower() not in (job.location or "").lower():
            if job.work_mode != WorkMode.REMOTE:
                return False
        if query.work_modes and job.work_mode not in query.work_modes:
            return False
        if query.job_types and job.job_type not in query.job_types:
            return False
        return True

    return [job for job in listings if matches(job)][: query.max_results]


def rank_jobs(listings: list[JobListing], resume_profile: ResumeProfile) -> list[JobFitScore]:
    return sorted(
        [score_job(job, resume_profile) for job in listings],
        key=lambda item: item.score,
        reverse=True,
    )


def score_job(job: JobListing, resume_profile: ResumeProfile) -> JobFitScore:
    resume_skills = {skill.lower() for skill in resume_profile.skills}
    job_requirements = {item.lower() for item in job.requirements}
    overlap = len(resume_skills & job_requirements)
    total_requirements = max(len(job_requirements), 1)
    skill_match = min(10.0, round((overlap / total_requirements) * 10, 1)) if resume_skills else 6.0

    seniority_match = 8.0
    if resume_profile.years_experience is not None and "senior" in job.title.lower():
        seniority_match = 9.0 if resume_profile.years_experience >= 5 else 5.0

    preferred_locations = [location.lower() for location in resume_profile.preferred_locations]
    location_match = 6.0
    if not preferred_locations:
        location_match = 7.5
    elif any(location in (job.location or "").lower() for location in preferred_locations):
        location_match = 10.0
    elif job.work_mode == WorkMode.REMOTE:
        location_match = 8.5

    compensation_match = 7.0
    if resume_profile.salary_floor and job.compensation and job.compensation.max_amount:
        compensation_match = 9.0 if job.compensation.max_amount >= resume_profile.salary_floor else 4.5

    summary_text = f"{resume_profile.summary} {resume_profile.title or ''}".lower()
    interest_match = 7.0
    if any(term in summary_text for term in ["ai", "agent", "python"]):
        interest_match = 8.5
    if "consultant" in job.title.lower():
        interest_match -= 1.0

    breakdown = JobScoreBreakdown(
        skill_match=skill_match,
        seniority_match=seniority_match,
        location_match=location_match,
        compensation_match=compensation_match,
        interest_match=max(0.0, min(10.0, interest_match)),
    )
    score = round(mean(breakdown.model_dump().values()), 2)

    strengths: list[str] = []
    risks: list[str] = []
    if skill_match >= 8:
        strengths.append("Strong requirement overlap with your stated skills.")
    if location_match >= 8:
        strengths.append("Location and work mode line up with current preferences.")
    if compensation_match >= 8:
        strengths.append("Compensation clears your stated floor.")
    if skill_match < 6:
        risks.append("Requirement overlap is still thin and may need stronger proof points.")
    if "consultant" in job.title.lower():
        risks.append("Role leans client-facing more than a pure builder track.")
    if job.work_mode == WorkMode.ONSITE:
        risks.append("Onsite expectation may reduce flexibility.")

    return JobFitScore(
        job=job,
        breakdown=breakdown,
        score=score,
        rationale=f"{job.title} at {job.company} scored {score}/10 based on fit, location, and compensation.",
        strengths=strengths,
        risks=risks,
    )


def draft_application(
    job: JobListing,
    resume_profile: ResumeProfile,
    fit_score: JobFitScore,
) -> ApplicationDraft:
    key_points = [
        f"Emphasize {resume_profile.title or 'your engineering background'} in relation to {job.title}.",
        f"Show evidence for: {', '.join(job.requirements[:3]) or 'role requirements'}.",
        f"Address this fit score directly: {fit_score.score}/10 with concrete examples.",
    ]
    cover_letter = (
        f"Dear {job.company} hiring team,\n\n"
        f"I am applying for the {job.title} role. My background aligns well with your focus on "
        f"{', '.join(job.requirements[:3]) or 'building strong products'}, and I have been working on "
        f"{resume_profile.summary}.\n\n"
        f"I am especially interested in this opportunity because it combines {job.work_mode.value} work with "
        f"practical ownership of production systems. I would bring a clear bias toward execution, measurable outcomes, "
        f"and clean delivery.\n\n"
        f"Thank you for your consideration.\n"
    )
    missing_information: list[str] = []
    if not resume_profile.candidate_name:
        missing_information.append("Candidate name")
    if not resume_profile.skills:
        missing_information.append("Detailed skills list")

    return ApplicationDraft(
        job=job,
        resume_profile=resume_profile,
        tailored_summary=fit_score.rationale,
        cover_letter=cover_letter,
        key_points=key_points,
        missing_information=missing_information,
        status=ApplicationStatus.DRAFTED,
    )

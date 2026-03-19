from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applyr.agents.job import JobSearchQuery, ResumeProfile, run_job_workflow


def main() -> None:
    query = JobSearchQuery(
        keywords=["software engineer", "python", "ai"],
        location="Toronto",
        max_results=10,
    )
    resume_profile = ResumeProfile(
        candidate_name="Tedros",
        title="Software Engineer",
        summary="experienced software engineer focused on Python, AI agents, and shipping practical products",
        skills=["Python", "LLMs", "APIs", "Evaluation", "Automation"],
        years_experience=6,
        preferred_locations=["Toronto", "Remote"],
        salary_floor=140000,
    )
    result = run_job_workflow(query, resume_profile)

    print("Top job matches:\n")
    for item in result.scored_jobs[:3]:
        print(f"- {item.job.title} @ {item.job.company} [{item.score}/10]")
        print(f"  {item.rationale}")

    print("\nDraft artifacts:\n")
    for draft in result.drafts:
        print(f"- {draft.job.title} @ {draft.job.company}")
        print(f"  Missing info: {', '.join(draft.missing_information) or 'none'}")


if __name__ == "__main__":
    main()

from pathlib import Path
from typing import Annotated

import typer

from applyr.agents.job import (
    JobSearchQuery,
    ResumeProfile,
    evaluate_job_workflow,
    load_job_fixture,
    run_job_workflow,
    submit_applications,
)
from applyr.agents.research import (
    Platform,
    ResearchQuery,
    evaluate_research_workflow,
    load_research_fixture,
    run_research_graph,
    run_research_workflow,
)
from applyr.core.config import get_settings

app = typer.Typer(help="Applyr CLI")
jobs_app = typer.Typer(help="Job application workflows")
research_app = typer.Typer(help="Market research workflows")

app.add_typer(jobs_app, name="jobs")
app.add_typer(research_app, name="research")


@app.callback()
def main_callback() -> None:
    """Root CLI callback."""


@jobs_app.command("status")
def jobs_status() -> None:
    settings = get_settings()
    typer.echo(
        f"jobs agent scaffold ready | openai={'set' if settings.openai_api_key else 'missing'} | "
        f"tavily={'set' if settings.tavily_api_key else 'missing'}"
    )


@research_app.command("status")
def research_status() -> None:
    settings = get_settings()
    typer.echo(
        f"research agent scaffold ready | openai={'set' if settings.openai_api_key else 'missing'} | "
        f"youtube={'set' if settings.youtube_api_key else 'missing'}"
    )


@jobs_app.command("run")
def jobs_run(
    keywords: Annotated[list[str], typer.Option("--keyword", "-k")] = ["python", "ai"],
    location: Annotated[str, typer.Option("--location", "-l")] = "Toronto",
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    limit: Annotated[int, typer.Option("--limit")] = 3,
) -> None:
    query = JobSearchQuery(keywords=keywords, location=location, max_results=10)
    resume_profile = ResumeProfile(
        candidate_name="Tedros",
        title="Software Engineer",
        summary="experienced software engineer focused on Python, AI agents, and shipping practical products",
        skills=["Python", "LLMs", "APIs", "Evaluation", "Automation"],
        years_experience=6,
        preferred_locations=["Toronto", "Remote"],
        salary_floor=140000,
    )
    seed_listings = load_job_fixture(fixture) if fixture else None
    result = run_job_workflow(query, resume_profile, limit=limit, seed_listings=seed_listings)

    typer.echo("Top job matches:\n")
    for item in result.scored_jobs[:limit]:
        typer.echo(f"- {item.job.title} @ {item.job.company} [{item.score}/10]")
        typer.echo(f"  {item.rationale}")

    typer.echo("\nDraft artifacts:\n")
    for draft in result.drafts:
        typer.echo(f"- {draft.job.title} @ {draft.job.company}")
        typer.echo(f"  Missing info: {', '.join(draft.missing_information) or 'none'}")


@jobs_app.command("eval")
def jobs_eval(
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
) -> None:
    query = JobSearchQuery(keywords=["python", "ai"], location="Toronto", max_results=10)
    resume_profile = ResumeProfile(
        candidate_name="Tedros",
        title="Software Engineer",
        summary="experienced software engineer focused on Python, AI agents, and shipping practical products",
        skills=["Python", "LLMs", "APIs", "Evaluation", "Automation"],
        years_experience=6,
        preferred_locations=["Toronto", "Remote"],
        salary_floor=140000,
    )
    seed_listings = load_job_fixture(fixture) if fixture else None
    result = run_job_workflow(query, resume_profile, seed_listings=seed_listings)
    evaluation = evaluate_job_workflow(result)
    typer.echo(evaluation.model_dump_json(indent=2))


@jobs_app.command("submit")
def jobs_submit(
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    confirm_submit: Annotated[bool, typer.Option("--confirm-submit")] = False,
) -> None:
    query = JobSearchQuery(keywords=["python", "ai"], location="Toronto", max_results=10)
    resume_profile = ResumeProfile(
        candidate_name="Tedros",
        title="Software Engineer",
        summary="experienced software engineer focused on Python, AI agents, and shipping practical products",
        skills=["Python", "LLMs", "APIs", "Evaluation", "Automation"],
        years_experience=6,
        preferred_locations=["Toronto", "Remote"],
        salary_floor=140000,
    )
    seed_listings = load_job_fixture(fixture) if fixture else None
    result = run_job_workflow(query, resume_profile, seed_listings=seed_listings)
    submission = submit_applications(result.drafts, confirm_submit=confirm_submit)
    typer.echo(submission.model_dump_json(indent=2))


@research_app.command("run")
def research_run(
    topic: Annotated[str, typer.Option("--topic", "-t")] = "AI agent building for beginners",
    audience: Annotated[str, typer.Option("--audience")] = "Developers and creators entering the AI automation space",
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    limit: Annotated[int, typer.Option("--limit")] = 3,
) -> None:
    query = ResearchQuery(
        topic=topic,
        audience=audience,
        goals=["Identify topics with demand", "Generate useful content briefs"],
        platforms=[Platform.WEB, Platform.YOUTUBE],
        max_results_per_source=5,
    )
    seed_signals = load_research_fixture(fixture) if fixture else None
    result = run_research_workflow(query, limit=limit, seed_signals=seed_signals)

    typer.echo("Top market opportunities:\n")
    for cluster in result.clusters[:limit]:
        typer.echo(
            f"- {cluster.name} | opportunity={cluster.opportunity_score}/10 | "
            f"competition={cluster.competition_level}/10"
        )

    typer.echo("\nContent briefs:\n")
    for brief in result.briefs[:limit]:
        typer.echo(f"- {brief.title} [{brief.score}/10]")
        typer.echo(f"  Hook: {brief.hook}")
        typer.echo(f"  Keyword: {brief.primary_keyword}")


@research_app.command("eval")
def research_eval(
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
) -> None:
    query = ResearchQuery(
        topic="AI agent building for beginners",
        audience="Developers and creators entering the AI automation space",
        goals=["Identify topics with demand", "Generate useful content briefs"],
        platforms=[Platform.WEB, Platform.YOUTUBE],
        max_results_per_source=5,
    )
    seed_signals = load_research_fixture(fixture) if fixture else None
    result = run_research_workflow(query, seed_signals=seed_signals)
    evaluation = evaluate_research_workflow(result)
    typer.echo(evaluation.model_dump_json(indent=2))


@research_app.command("graph")
def research_graph(
    topic: Annotated[str, typer.Option("--topic", "-t")] = "AI agent building for beginners",
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
) -> None:
    query = ResearchQuery(
        topic=topic,
        audience="Developers and creators entering the AI automation space",
        goals=["Identify topics with demand", "Generate useful content briefs"],
        platforms=[Platform.WEB, Platform.YOUTUBE],
        max_results_per_source=5,
    )
    seed_signals = load_research_fixture(fixture) if fixture else None
    state = run_research_graph(query, seed_signals=seed_signals)
    typer.echo(
        f"graph complete | signals={len(state['signals'])} | "
        f"clusters={len(state['clusters'])} | briefs={len(state['briefs'])}"
    )


def main() -> None:
    app()

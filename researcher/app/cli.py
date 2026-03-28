from pathlib import Path
from typing import Annotated

import typer

from core.config import get_settings
from researcher.evals import evaluate_signal_workflow
from researcher.fixtures import load_signal_fixture
from researcher.models import SignalQuery, SourceType
from researcher.workflow.orchestration import run_signal_graph
from researcher.workflow.pipeline import run_signal_workflow
from researcher.workflow.rendering import format_terminal_report, serialize_workflow_result

app = typer.Typer(help="Applyr CLI")


@app.callback()
def main_callback() -> None:
    """Root CLI callback."""


@app.command("status")
def status() -> None:
    settings = get_settings()
    typer.echo(
        f"researcher ready | anthropic={'set' if settings.anthropic_api_key else 'missing'} | "
        f"cache_dir={settings.cache_dir}"
    )


@app.command("run")
def run(
    verticals: Annotated[list[str], typer.Option("--vertical", "-v")] = [
        "spreadsheet",
        "clinic",
        "service",
    ],
    subreddits: Annotated[list[str], typer.Option("--subreddit")] = [
        "smallbusiness",
        "entrepreneur",
        "personaltraining",
    ],
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    limit: Annotated[int, typer.Option("--limit")] = 5,
    as_json: Annotated[bool, typer.Option("--json")] = False,
    use_claude: Annotated[bool, typer.Option("--use-claude")] = False,
    reddit_only: Annotated[bool, typer.Option("--reddit-only")] = False,
) -> None:
    query = SignalQuery(
        verticals=verticals,
        subreddits=subreddits,
        review_sites=[] if reddit_only else [SourceType.G2, SourceType.CAPTERRA],
        max_results_per_source=limit,
        use_claude=use_claude,
    )
    seed_records = load_signal_fixture(fixture) if fixture else None
    result = run_signal_workflow(query, limit=limit, seed_records=seed_records)
    typer.echo(serialize_workflow_result(result) if as_json else format_terminal_report(result, limit=limit))


@app.command("eval")
def eval(
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    reddit_only: Annotated[bool, typer.Option("--reddit-only")] = False,
) -> None:
    query = SignalQuery(
        verticals=["spreadsheet", "clinic", "service"],
        review_sites=[] if reddit_only else [SourceType.G2, SourceType.CAPTERRA],
    )
    seed_records = load_signal_fixture(fixture) if fixture else None
    result = run_signal_workflow(query, seed_records=seed_records)
    evaluation = evaluate_signal_workflow(result)
    typer.echo(evaluation.model_dump_json(indent=2))


@app.command("graph")
def graph(
    fixture: Annotated[Path | None, typer.Option("--fixture")] = None,
    reddit_only: Annotated[bool, typer.Option("--reddit-only")] = False,
) -> None:
    query = SignalQuery(
        verticals=["spreadsheet", "clinic", "service"],
        review_sites=[] if reddit_only else [SourceType.G2, SourceType.CAPTERRA],
    )
    seed_records = load_signal_fixture(fixture) if fixture else None
    state = run_signal_graph(query, seed_records=seed_records)
    typer.echo(
        f"graph complete | collected={len(state['collected_records'])} | "
        f"normalized={len(state['normalized_records'])} | ranked={len(state['opportunities'])}"
    )


def main() -> None:
    app()

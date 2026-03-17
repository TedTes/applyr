import typer

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


def main() -> None:
    app()

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applyr.agents.research import Platform, ResearchQuery, run_research_workflow


def main() -> None:
    query = ResearchQuery(
        topic="AI agent building for beginners",
        audience="Developers and creators entering the AI automation space",
        goals=["Identify topics with demand", "Generate useful content briefs"],
        platforms=[Platform.WEB, Platform.YOUTUBE],
        max_results_per_source=5,
    )
    result = run_research_workflow(query)

    print("Top market opportunities:\n")
    for cluster in result.clusters:
        print(
            f"- {cluster.name} | opportunity={cluster.opportunity_score}/10 | "
            f"competition={cluster.competition_level}/10"
        )

    print("\nContent briefs:\n")
    for brief in result.briefs[:3]:
        print(f"- {brief.title} [{brief.score}/10]")
        print(f"  Hook: {brief.hook}")
        print(f"  Keyword: {brief.primary_keyword}")


if __name__ == "__main__":
    main()

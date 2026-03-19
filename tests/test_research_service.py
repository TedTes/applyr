from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applyr.agents.research import Platform, ResearchQuery, run_research_workflow
from applyr.agents.research.evals import evaluate_research_workflow
from applyr.agents.research.orchestration import run_research_graph
from applyr.agents.research.service import load_research_fixture


FIXTURE_PATH = ROOT / "data" / "fixtures" / "research_signals.json"


class ResearchServiceTests(unittest.TestCase):
    def test_load_research_fixture(self) -> None:
        signals = load_research_fixture(FIXTURE_PATH)
        self.assertEqual(len(signals), 5)
        self.assertEqual(signals[0].platform.value, "youtube")

    def test_research_workflow_produces_multiple_clusters(self) -> None:
        result = run_research_workflow(
            ResearchQuery(
                topic="AI agent building for beginners",
                platforms=[Platform.WEB, Platform.YOUTUBE],
            ),
            seed_signals=load_research_fixture(FIXTURE_PATH),
        )
        self.assertEqual(
            [cluster.name for cluster in result.clusters],
            ["Beginner Tutorials", "Tooling Comparisons", "Production Use Cases"],
        )
        self.assertEqual(len(result.briefs), 3)
        self.assertGreater(result.briefs[0].score, 0)
        evaluation = evaluate_research_workflow(result)
        self.assertEqual(evaluation.clusters_found, 3)
        self.assertGreater(evaluation.average_brief_score, 0)

    def test_research_graph_runs_end_to_end(self) -> None:
        state = run_research_graph(
            ResearchQuery(
                topic="AI agent building for beginners",
                platforms=[Platform.WEB, Platform.YOUTUBE],
            ),
            seed_signals=load_research_fixture(FIXTURE_PATH),
        )
        self.assertEqual(len(state["signals"]), 5)
        self.assertEqual(len(state["clusters"]), 3)
        self.assertEqual(len(state["briefs"]), 3)

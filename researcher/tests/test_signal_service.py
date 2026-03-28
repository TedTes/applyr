from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parents[0]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from researcher import SignalQuery, SourceType, format_terminal_report, run_signal_graph, run_signal_workflow
from researcher.evals import evaluate_signal_workflow
from researcher.service import load_signal_fixture, normalize_records, parse_reddit_response
from researcher.workflow.scorer import score_record


FIXTURE_PATH = ROOT / "data" / "fixtures" / "saas_signals.json"


class SignalServiceTests(unittest.TestCase):
    def test_load_signal_fixture(self) -> None:
        records = load_signal_fixture(FIXTURE_PATH)
        self.assertEqual(len(records), 4)
        self.assertEqual(records[0].source.value, "reddit")

    def test_signal_workflow_ranks_fixture_records(self) -> None:
        result = run_signal_workflow(
            SignalQuery(
                verticals=["spreadsheet", "clinic", "service"],
                max_results_per_source=5,
            ),
            seed_records=load_signal_fixture(FIXTURE_PATH),
        )
        self.assertEqual(len(result.collected_records), 4)
        self.assertEqual(len(result.opportunities), 4)
        self.assertGreaterEqual(result.opportunities[0].total_score, result.opportunities[-1].total_score)
        self.assertIn(result.opportunities[0].record.source, {SourceType.REDDIT, SourceType.G2, SourceType.CAPTERRA})

        evaluation = evaluate_signal_workflow(result)
        self.assertEqual(evaluation.collected_records, 4)
        self.assertGreater(evaluation.average_total_score, 0)

    def test_normalize_records_deduplicates_by_url(self) -> None:
        records = load_signal_fixture(FIXTURE_PATH)
        duplicated = [records[0], records[0], *records[1:]]
        normalized = normalize_records(duplicated)
        self.assertEqual(len(normalized), 4)

    def test_signal_graph_runs_end_to_end(self) -> None:
        state = run_signal_graph(
            SignalQuery(verticals=["spreadsheet", "clinic", "service"]),
            seed_records=load_signal_fixture(FIXTURE_PATH),
        )
        self.assertEqual(len(state["collected_records"]), 4)
        self.assertEqual(len(state["normalized_records"]), 4)
        self.assertEqual(len(state["opportunities"]), 4)

    def test_terminal_report_contains_ranked_output(self) -> None:
        result = run_signal_workflow(
            SignalQuery(verticals=["spreadsheet", "clinic", "service"]),
            seed_records=load_signal_fixture(FIXTURE_PATH),
        )
        report = format_terminal_report(result, limit=2)
        self.assertIn("SaaS Signal opportunities", report)
        self.assertIn("/50", report)

    def test_parse_reddit_response_maps_live_payload_shape(self) -> None:
        payload = {
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc123",
                            "title": "We still track referrals in a spreadsheet",
                            "selftext": "My clinic manager manually does this every week.",
                            "permalink": "/r/healthcare/comments/abc123/example/",
                            "score": 128,
                            "created_utc": 1700000000,
                            "subreddit": "healthcare",
                            "author": "founder1",
                            "num_comments": 22,
                        }
                    }
                ]
            }
        }

        records = parse_reddit_response(payload, subreddit="healthcare")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].source, SourceType.REDDIT)
        self.assertEqual(str(records[0].url), "https://www.reddit.com/r/healthcare/comments/abc123/example/")
        self.assertEqual(records[0].metadata["subreddit"], "healthcare")

    def test_claude_flag_falls_back_to_heuristic_without_key(self) -> None:
        record = load_signal_fixture(FIXTURE_PATH)[0]
        scored = score_record(
            SignalQuery(
                verticals=["spreadsheet"],
                use_claude=True,
            ),
            record,
        )
        self.assertGreater(scored.total_score, 0)
        self.assertTrue(scored.pain_summary)

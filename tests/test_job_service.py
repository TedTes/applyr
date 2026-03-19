from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from applyr.agents.job import JobSearchQuery, ResumeProfile, run_job_workflow, search_jobs
from applyr.agents.job.evals import evaluate_job_workflow
from applyr.agents.job.service import load_job_fixture
from applyr.agents.job.submission import submit_applications


FIXTURE_PATH = ROOT / "data" / "fixtures" / "job_listings.json"


class JobServiceTests(unittest.TestCase):
    def test_load_job_fixture(self) -> None:
        listings = load_job_fixture(FIXTURE_PATH)
        self.assertEqual(len(listings), 4)
        self.assertEqual(listings[0].company, "Northstar Labs")

    def test_search_jobs_uses_fixture_data(self) -> None:
        query = JobSearchQuery(keywords=["python", "ai"], location="Toronto")
        listings = search_jobs(query, seed_listings=load_job_fixture(FIXTURE_PATH))
        self.assertTrue(listings)
        self.assertIn("Senior Python AI Engineer", [item.title for item in listings])

    def test_job_workflow_returns_ranked_drafts(self) -> None:
        result = run_job_workflow(
            JobSearchQuery(keywords=["python", "ai"], location="Toronto"),
            ResumeProfile(
                summary="Python AI engineer",
                skills=["Python", "LLMs", "APIs", "Evaluation"],
                preferred_locations=["Toronto", "Remote"],
                salary_floor=140000,
            ),
            seed_listings=load_job_fixture(FIXTURE_PATH),
        )
        self.assertGreaterEqual(len(result.scored_jobs), 2)
        self.assertGreaterEqual(result.scored_jobs[0].score, result.scored_jobs[1].score)
        self.assertEqual(len(result.drafts), 3)
        self.assertEqual(result.drafts[0].job.title, result.scored_jobs[0].job.title)
        evaluation = evaluate_job_workflow(result)
        self.assertGreater(evaluation.average_fit_score, 0)
        self.assertEqual(evaluation.ready_rate, 0.0)

    def test_submission_gate_blocks_without_confirmation(self) -> None:
        result = run_job_workflow(
            JobSearchQuery(keywords=["python", "ai"], location="Toronto"),
            ResumeProfile(summary="Python AI engineer", skills=["Python"], candidate_name="Tedros"),
            seed_listings=load_job_fixture(FIXTURE_PATH),
        )
        submission = submit_applications(result.drafts, confirm_submit=False)
        self.assertFalse(submission.confirmed)
        self.assertTrue(all(not item.submitted for item in submission.results))

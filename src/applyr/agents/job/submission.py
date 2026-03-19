from pydantic import Field

from applyr.agents.job.models import ApplicationDraft
from applyr.core.models import ApplyrBaseModel


class SubmissionResult(ApplyrBaseModel):
    company: str
    job_title: str
    submitted: bool
    reason: str


class SubmissionBatchResult(ApplyrBaseModel):
    confirmed: bool
    results: list[SubmissionResult] = Field(default_factory=list)


def submit_applications(drafts: list[ApplicationDraft], confirm_submit: bool = False) -> SubmissionBatchResult:
    if not confirm_submit:
        return SubmissionBatchResult(
            confirmed=False,
            results=[
                SubmissionResult(
                    company=draft.job.company,
                    job_title=draft.job.title,
                    submitted=False,
                    reason="Submission blocked until confirm_submit=True.",
                )
                for draft in drafts
            ],
        )

    return SubmissionBatchResult(
        confirmed=True,
        results=[
            SubmissionResult(
                company=draft.job.company,
                job_title=draft.job.title,
                submitted=not draft.missing_information,
                reason="Submitted via approval gate." if not draft.missing_information else "Missing required information.",
            )
            for draft in drafts
        ],
    )

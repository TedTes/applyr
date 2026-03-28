from __future__ import annotations

import json
from pathlib import Path

from core.models import SourceRef
from core.retry import retry
from researcher.models import SignalRecord, SourceType


@retry()
def default_signal_seed() -> list[SignalRecord]:
    return [
        SignalRecord(
            id="reddit_pt_001",
            source=SourceType.REDDIT,
            title="How do you track client check-ins without a spreadsheet?",
            body="We still manually review every form response and then copy the notes into a spreadsheet for follow-up. It takes me hours every week.",
            url="https://reddit.com/r/personaltraining/comments/example1",
            source_ref=SourceRef(name="Reddit", url="https://reddit.com/r/personaltraining"),
            source_score=847,
            metadata={"subreddit": "personaltraining", "upvotes": 847},
        ),
        SignalRecord(
            id="reddit_bookkeeping_001",
            source=SourceType.REDDIT,
            title="Any tool for reconciling invoices from contractors?",
            body="Right now my ops manager manually reconciles invoices, checks bank transfers, and updates a spreadsheet. Wish there was a tool that handled the boring part.",
            url="https://reddit.com/r/smallbusiness/comments/example2",
            source_ref=SourceRef(name="Reddit", url="https://reddit.com/r/smallbusiness"),
            source_score=612,
            metadata={"subreddit": "smallbusiness", "upvotes": 612},
        ),
        SignalRecord(
            id="reddit_field_001",
            source=SourceType.REDDIT,
            title="We use a spreadsheet for every field-service callback",
            body="Dispatch is still manual and our coordinators spend half the day moving jobs around. The spreadsheet works until it does not.",
            url="https://reddit.com/r/Entrepreneur/comments/example3",
            source_ref=SourceRef(name="Reddit", url="https://reddit.com/r/Entrepreneur"),
            source_score=455,
            metadata={"subreddit": "Entrepreneur", "upvotes": 455},
        ),
        SignalRecord(
            id="g2_crm_001",
            source=SourceType.G2,
            title="3-star review: CRM still forces manual follow-up tracking",
            body="The platform is fine for storing contacts, but our team exports records every Friday to manually assign next actions. That gap causes dropped leads.",
            url="https://www.g2.com/products/example-crm/reviews/review-1",
            source_ref=SourceRef(name="G2", url="https://www.g2.com"),
            source_score=3,
            metadata={"category": "crm", "star_rating": 3},
        ),
        SignalRecord(
            id="g2_clinic_001",
            source=SourceType.G2,
            title="3-star review: clinic intake requires duplicate data entry",
            body="Scheduling works, but front-desk staff still re-enter insurance and intake data by hand. It is a daily task and easy to mess up.",
            url="https://www.g2.com/products/example-clinic/reviews/review-2",
            source_ref=SourceRef(name="G2", url="https://www.g2.com"),
            source_score=3,
            metadata={"category": "healthcare_admin", "star_rating": 3},
        ),
        SignalRecord(
            id="capterra_field_001",
            source=SourceType.CAPTERRA,
            title="3-star review: job scheduling breaks on recurring service visits",
            body="Recurring jobs are painful. Staff manually rebuild routes and call customers one by one when something changes.",
            url="https://www.capterra.com/p/example/reviews/1",
            source_ref=SourceRef(name="Capterra", url="https://www.capterra.com"),
            source_score=3,
            metadata={"category": "field_service", "star_rating": 3},
        ),
    ]


def load_signal_fixture(path: str | Path) -> list[SignalRecord]:
    payload = json.loads(Path(path).read_text())
    return [SignalRecord.model_validate(item) for item in payload]

from researcher.models import SignalRecord


def normalize_records(records: list[SignalRecord]) -> list[SignalRecord]:
    deduped: dict[str, SignalRecord] = {}
    for record in records:
        deduped.setdefault(_record_key(record), record)
    return list(deduped.values())


def _record_key(record: SignalRecord) -> str:
    return str(record.url).rstrip("/")

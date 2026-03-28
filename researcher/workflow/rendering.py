import json

from researcher.workflow.pipeline import SignalWorkflowResult


def format_terminal_report(result: SignalWorkflowResult, limit: int = 10) -> str:
    lines = [
        "SaaS Signal opportunities",
        "",
    ]
    for index, opportunity in enumerate(result.opportunities[:limit], start=1):
        record = opportunity.record
        lines.append(
            f"{index}. {record.title} [{record.source.value}] {opportunity.total_score}/50"
        )
        lines.append(f"   Summary: {opportunity.pain_summary}")
        lines.append(f"   URL: {record.url}")
        lines.append(
            "   Breakdown: "
            f"pain={opportunity.breakdown.pain_intensity}/10, "
            f"pay={opportunity.breakdown.willingness_to_pay}/10, "
            f"frequency={opportunity.breakdown.frequency}/10, "
            f"market={opportunity.breakdown.market_size}/10, "
            f"gap={opportunity.breakdown.competition_gap}/10"
        )
        lines.append("")
    return "\n".join(lines).rstrip()


def serialize_workflow_result(result: SignalWorkflowResult) -> str:
    payload = {
        "query": result.query.model_dump(mode="json"),
        "collected_records": [item.model_dump(mode="json") for item in result.collected_records],
        "normalized_records": [item.model_dump(mode="json") for item in result.normalized_records],
        "opportunities": [item.model_dump(mode="json") for item in result.opportunities],
    }
    return json.dumps(payload, indent=2)

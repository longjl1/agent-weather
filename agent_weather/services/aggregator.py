from agent_weather.models import AgentRun, AggregateMetrics


def aggregate_runs(runs: list[AgentRun]) -> AggregateMetrics:
    total_runs = len(runs)
    if total_runs == 0:
        return AggregateMetrics(
            total_runs=0,
            success_rate=0.0,
            avg_duration_ms=0.0,
            tool_error_rate=0.0,
            avg_retries=0.0,
            avg_context_tokens=0.0,
            avg_output_quality=0.0,
            avg_adherence=0.0,
            avg_confidence=0.0,
        )

    total_tool_calls = sum(run.tool_calls for run in runs)
    total_tool_errors = sum(run.tool_errors for run in runs)

    return AggregateMetrics(
        total_runs=total_runs,
        success_rate=sum(1 for run in runs if run.success) / total_runs,
        avg_duration_ms=sum(run.duration_ms for run in runs) / total_runs,
        tool_error_rate=(total_tool_errors / total_tool_calls) if total_tool_calls else 0.0,
        avg_retries=sum(run.retries for run in runs) / total_runs,
        avg_context_tokens=sum(run.context_tokens for run in runs) / total_runs,
        avg_output_quality=sum(run.output_quality for run in runs) / total_runs,
        avg_adherence=sum(run.adherence for run in runs) / total_runs,
        avg_confidence=sum(run.confidence for run in runs) / total_runs,
    )

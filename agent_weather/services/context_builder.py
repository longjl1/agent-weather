from agent_weather.config import AppConfig
from agent_weather.models import AgentRun, AggregateMetrics, EvaluationContext


def build_evaluation_context(
    runs: list[AgentRun],
    metrics: AggregateMetrics,
    config: AppConfig,
) -> EvaluationContext:
    behavior_signals: list[str] = []
    recent_failures: list[str] = []

    if metrics.avg_retries > 1.5:
        behavior_signals.append("often retries before reaching a stable result")
    if metrics.avg_context_tokens > 12000:
        behavior_signals.append("context grows quickly on multi-step tasks")
    if metrics.avg_adherence < 0.8:
        behavior_signals.append("sometimes loses formatting or instruction precision")
    if metrics.avg_output_quality > 0.82:
        behavior_signals.append("can produce strong results when scope remains clear")

    for run in runs:
        if not run.success and run.notes:
            recent_failures.append(run.notes)

    return EvaluationContext(
        agent_name=config.agent_name,
        window_label=f"last_{len(runs)}_runs",
        metrics={
            "success_rate": metrics.success_rate,
            "avg_duration_ms": metrics.avg_duration_ms,
            "tool_error_rate": metrics.tool_error_rate,
            "avg_retries": metrics.avg_retries,
            "avg_context_tokens": metrics.avg_context_tokens,
            "avg_output_quality": metrics.avg_output_quality,
            "avg_adherence": metrics.avg_adherence,
            "avg_confidence": metrics.avg_confidence,
        },
        behavior_signals=behavior_signals,
        recent_failures=recent_failures,
    )

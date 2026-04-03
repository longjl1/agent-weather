from agent_weather.models import AggregateMetrics, WeatherReport
from agent_weather.services.skill_suggestions import suggest_skills


def classify_weather(metrics: AggregateMetrics) -> WeatherReport:
    weather = "cloudy"
    score = 0.62
    summary = "The agent is functional, but some instability is showing up in execution quality."
    risks: list[str] = []
    strengths: list[str] = []

    if metrics.success_rate < 0.45 and metrics.tool_error_rate > 0.2:
        weather = "storm"
        score = 0.22
        summary = "The agent is currently unstable, with repeated failure signals and tool friction."
    elif metrics.success_rate < 0.65 and metrics.avg_retries > 2:
        weather = "rainy"
        score = 0.43
        summary = "The agent can still complete work, but retries and recovery overhead are dragging it down."
    elif metrics.avg_adherence < 0.75 and metrics.avg_context_tokens > 12000:
        weather = "windy"
        score = 0.48
        summary = "The agent is drifting under context load and may lose instruction precision."
    elif metrics.success_rate >= 0.7 and metrics.avg_confidence < 0.6:
        weather = "fog"
        score = 0.58
        summary = "The outputs are often acceptable, but confidence and explainability remain weak."
    elif (
        metrics.success_rate > 0.9
        and metrics.tool_error_rate < 0.08
        and metrics.avg_output_quality > 0.88
    ):
        weather = "aurora"
        score = 0.96
        summary = "The agent is operating at an unusually strong level with high quality and resilience."
    elif (
        metrics.success_rate > 0.82
        and metrics.tool_error_rate < 0.12
        and metrics.avg_adherence > 0.84
    ):
        weather = "sunny"
        score = 0.87
        summary = "The agent is stable, reliable, and handling most tasks with healthy execution."

    if metrics.tool_error_rate > 0.18:
        risks.append("tool failures are materially affecting run stability")
    if metrics.avg_context_tokens > 12000:
        risks.append("context size may be contributing to drift or slower recovery")
    if metrics.avg_adherence < 0.8:
        risks.append("instruction adherence is below the desired operating range")

    if metrics.avg_output_quality > 0.8:
        strengths.append("output quality remains solid on clear tasks")
    if metrics.success_rate > 0.7:
        strengths.append("the agent still completes a majority of recent runs")
    if metrics.avg_confidence > 0.72:
        strengths.append("the agent shows relatively stable self-confidence")

    return WeatherReport(
        weather=weather,
        score=score,
        summary=summary,
        risks=risks,
        strengths=strengths,
        suggestions=suggest_skills(metrics),
    )

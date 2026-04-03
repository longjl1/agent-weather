from agent_weather.models import EvaluationContext, WeatherReport


def build_evaluator_prompt(context: EvaluationContext, weather: WeatherReport) -> str:
    return f"""
You are an evaluator for a single-agent runtime.

You are given:
- a structured operating context
- a baseline weather classification

Your task:
1. confirm or refine the diagnosis
2. explain the current operating condition
3. identify top risks
4. identify top strengths
5. propose concrete improvement suggestions

Return strict JSON with:
- weather
- summary
- risks
- strengths
- suggestions

Context:
agent_name={context.agent_name}
window={context.window_label}
metrics={context.metrics}
behavior_signals={context.behavior_signals}
recent_failures={context.recent_failures}
baseline_weather={weather.weather}
baseline_summary={weather.summary}
""".strip()


def run_placeholder_evaluator(context: EvaluationContext, weather: WeatherReport) -> dict:
    return {
        "weather": weather.weather,
        "summary": weather.summary,
        "risks": weather.risks,
        "strengths": weather.strengths,
        "suggestions": [
            {
                "title": suggestion.title,
                "reason": suggestion.reason,
            }
            for suggestion in weather.suggestions
        ],
        "prompt_preview": build_evaluator_prompt(context, weather),
    }

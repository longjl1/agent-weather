from agent_weather.models import AgentRun


def load_mock_runs() -> list[AgentRun]:
    return [
        AgentRun(
            id="run-001",
            task="Summarize repo changes and propose a plan",
            started_at="2026-04-03T09:10:00Z",
            duration_ms=18200,
            success=True,
            tool_calls=6,
            tool_errors=1,
            retries=1,
            context_tokens=9200,
            output_quality=0.82,
            adherence=0.86,
            confidence=0.74,
            notes="Strong search and synthesis, minor formatting drift."
        ),
        AgentRun(
            id="run-002",
            task="Create a landing page from an existing design direction",
            started_at="2026-04-03T11:20:00Z",
            duration_ms=26400,
            success=True,
            tool_calls=9,
            tool_errors=2,
            retries=2,
            context_tokens=12800,
            output_quality=0.88,
            adherence=0.79,
            confidence=0.76,
            notes="Good implementation quality, slight scope expansion."
        ),
        AgentRun(
            id="run-003",
            task="Fix a failing build and verify the app",
            started_at="2026-04-03T12:40:00Z",
            duration_ms=34100,
            success=False,
            tool_calls=11,
            tool_errors=4,
            retries=3,
            context_tokens=14400,
            output_quality=0.52,
            adherence=0.73,
            confidence=0.48,
            notes="Build repair attempted but recovery was incomplete."
        ),
        AgentRun(
            id="run-004",
            task="Review a PR for regressions and testing gaps",
            started_at="2026-04-03T14:15:00Z",
            duration_ms=15700,
            success=True,
            tool_calls=5,
            tool_errors=0,
            retries=0,
            context_tokens=7600,
            output_quality=0.9,
            adherence=0.91,
            confidence=0.84,
            notes="Clear findings and good risk framing."
        ),
        AgentRun(
            id="run-005",
            task="Refactor a multi-file feature under time pressure",
            started_at="2026-04-03T15:30:00Z",
            duration_ms=38900,
            success=False,
            tool_calls=13,
            tool_errors=3,
            retries=4,
            context_tokens=17100,
            output_quality=0.49,
            adherence=0.68,
            confidence=0.44,
            notes="Context drift and incomplete finishing behavior."
        ),
    ]

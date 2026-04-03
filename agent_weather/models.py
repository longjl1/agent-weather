from dataclasses import dataclass, field
from typing import Literal


WeatherLabel = Literal["sunny", "cloudy", "windy", "rainy", "storm", "fog", "aurora"]


@dataclass
class AgentRun:
    id: str
    task: str
    started_at: str
    duration_ms: int
    success: bool
    tool_calls: int
    tool_errors: int
    retries: int
    context_tokens: int
    output_quality: float
    adherence: float
    confidence: float
    notes: str | None = None


@dataclass
class AggregateMetrics:
    total_runs: int
    success_rate: float
    avg_duration_ms: float
    tool_error_rate: float
    avg_retries: float
    avg_context_tokens: float
    avg_output_quality: float
    avg_adherence: float
    avg_confidence: float


@dataclass
class SkillSuggestion:
    title: str
    reason: str
    prompt_patch: str | None = None
    system_patch: str | None = None


@dataclass
class WeatherReport:
    weather: WeatherLabel
    score: float
    summary: str
    risks: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    suggestions: list[SkillSuggestion] = field(default_factory=list)


@dataclass
class EvaluationContext:
    agent_name: str
    window_label: str
    metrics: dict[str, float]
    behavior_signals: list[str]
    recent_failures: list[str]

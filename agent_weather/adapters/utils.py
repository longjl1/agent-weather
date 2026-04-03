from __future__ import annotations

from datetime import datetime
from pathlib import Path

from agent_weather.models import AgentRun


FAILURE_HINTS = (
    "error",
    "failed",
    "失败",
    "无法",
    "不能",
    "暂时不可用",
    "need more information",
    "i cannot",
)

HEDGE_HINTS = (
    "可能",
    "也许",
    "不确定",
    "无法确认",
    "could",
    "might",
    "unclear",
)


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None

    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def short_text(value: str | None, limit: int = 72) -> str:
    text = (value or "").strip().replace("\n", " ")
    if not text:
        return "Untitled run"
    return text[:limit] + ("..." if len(text) > limit else "")


def estimate_context_tokens(chunks: list[str]) -> int:
    total_chars = sum(len(chunk) for chunk in chunks)
    return max(1, round(total_chars / 4))


def count_failure_hints(chunks: list[str]) -> int:
    count = 0
    for chunk in chunks:
        lowered = chunk.lower()
        count += sum(1 for hint in FAILURE_HINTS if hint in lowered)
    return count


def estimate_confidence(chunks: list[str], success: bool) -> float:
    hedges = 0
    for chunk in chunks:
        lowered = chunk.lower()
        hedges += sum(1 for hint in HEDGE_HINTS if hint in lowered)

    base = 0.78 if success else 0.48
    return max(0.2, min(0.95, base - min(0.3, hedges * 0.05)))


def estimate_adherence(last_assistant_text: str, tool_errors: int, success: bool) -> float:
    structure_bonus = 0.08 if any(token in last_assistant_text for token in ("##", "-", "1.", "2.", "###")) else 0.0
    base = 0.84 if success else 0.66
    penalty = min(0.28, tool_errors * 0.06)
    return max(0.25, min(0.98, base + structure_bonus - penalty))


def estimate_quality(
    success: bool,
    tool_errors: int,
    assistant_messages: int,
    last_assistant_text: str,
) -> float:
    base = 0.82 if success else 0.5
    verbosity_bonus = 0.05 if len(last_assistant_text) > 180 else 0.0
    response_bonus = min(0.06, assistant_messages * 0.01)
    penalty = min(0.25, tool_errors * 0.05)
    return max(0.2, min(0.96, base + verbosity_bonus + response_bonus - penalty))


def derive_duration_ms(started_at: datetime | None, ended_at: datetime | None, messages_count: int) -> int:
    if started_at and ended_at and ended_at >= started_at:
        return max(1000, int((ended_at - started_at).total_seconds() * 1000))
    return max(5000, messages_count * 4500)


def build_notes(success: bool, tool_errors: int, retries: int, context_tokens: int) -> str:
    parts: list[str] = []
    parts.append("healthy run" if success else "unstable run")
    if tool_errors:
        parts.append(f"{tool_errors} failure signal(s)")
    if retries:
        parts.append(f"{retries} retry-like turn(s)")
    if context_tokens > 12000:
        parts.append("high context pressure")
    return ", ".join(parts)


def normalize_run(
    *,
    run_id: str,
    task: str,
    started_at: str,
    duration_ms: int,
    success: bool,
    tool_calls: int,
    tool_errors: int,
    retries: int,
    context_tokens: int,
    output_quality: float,
    adherence: float,
    confidence: float,
    notes: str,
) -> AgentRun:
    return AgentRun(
        id=run_id,
        task=task,
        started_at=started_at,
        duration_ms=duration_ms,
        success=success,
        tool_calls=tool_calls,
        tool_errors=tool_errors,
        retries=retries,
        context_tokens=context_tokens,
        output_quality=output_quality,
        adherence=adherence,
        confidence=confidence,
        notes=notes,
    )


def sorted_paths(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda item: item.stat().st_mtime, reverse=True)

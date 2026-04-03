from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from agent_weather.adapters.base import AdapterDescriptor, AdapterLoadResult, RuntimeAdapter
from agent_weather.adapters.utils import (
    build_notes,
    count_failure_hints,
    derive_duration_ms,
    estimate_adherence,
    estimate_confidence,
    estimate_context_tokens,
    estimate_quality,
    normalize_run,
    parse_timestamp,
    short_text,
    sorted_paths,
)


class SejuLiteAdapter(RuntimeAdapter):
    adapter_id = "seju-lite"
    label = "seju-lite"

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(r"d:\ProjectsCollection\seju-lite")
        self.sessions_dir = self.project_root / "workspace" / "sessions"

    def describe(self) -> AdapterDescriptor:
        if not self.project_root.exists():
            return AdapterDescriptor(
                adapter_id=self.adapter_id,
                label=self.label,
                status="missing",
                message="Project directory not found.",
                source_path=self._as_string(self.project_root),
            )

        if not self.sessions_dir.exists():
            return AdapterDescriptor(
                adapter_id=self.adapter_id,
                label=self.label,
                status="missing",
                message="Workspace sessions directory not found.",
                source_path=self._as_string(self.sessions_dir),
            )

        session_files = list(self.sessions_dir.glob("*.json"))
        return AdapterDescriptor(
            adapter_id=self.adapter_id,
            label=self.label,
            status="ready" if session_files else "empty",
            message=f"Detected {len(session_files)} local session file(s).",
            source_path=self._as_string(self.sessions_dir),
        )

    def load_runs(self, rolling_window: int) -> AdapterLoadResult:
        descriptor = self.describe()
        warnings: list[str] = []
        if descriptor.status != "ready":
            warnings.append(descriptor.message)
            return AdapterLoadResult(
                adapter_id=self.adapter_id,
                label=self.label,
                agent_name="seju-lite",
                runs=[],
                source_path=descriptor.source_path,
                warnings=warnings,
            )

        runs = []
        for session_path in sorted_paths(list(self.sessions_dir.glob("*.json")))[:rolling_window]:
            try:
                raw = json.loads(session_path.read_text(encoding="utf-8"))
            except Exception as exc:
                warnings.append(f"Failed to parse {session_path.name}: {exc}")
                continue

            messages = raw.get("messages") or []
            if not messages:
                continue

            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            tool_calls = sum(len(msg.get("tool_calls") or []) for msg in assistant_messages)
            text_chunks = [str(msg.get("content", "")) for msg in messages if msg.get("content")]
            assistant_chunks = [str(msg.get("content", "")) for msg in assistant_messages if msg.get("content")]

            first_user = next((msg for msg in messages if msg.get("role") == "user"), {})
            last_assistant_text = assistant_chunks[-1] if assistant_chunks else ""
            failure_signals = count_failure_hints(assistant_chunks[-3:] or assistant_chunks)
            retries = max(0, len(user_messages) - 1)
            success = bool(last_assistant_text) and failure_signals == 0

            started_dt = parse_timestamp(first_user.get("timestamp")) or parse_timestamp(raw.get("updated_at"))
            ended_dt = parse_timestamp(raw.get("updated_at")) or (
                parse_timestamp(messages[-1].get("timestamp")) if messages else None
            )
            started_at = (
                (started_dt or ended_dt).isoformat()
                if (started_dt or ended_dt)
                else datetime.fromtimestamp(session_path.stat().st_mtime).isoformat()
            )
            duration_ms = derive_duration_ms(started_dt, ended_dt, len(messages))
            context_tokens = estimate_context_tokens(text_chunks)
            adherence = estimate_adherence(last_assistant_text, failure_signals, success)
            confidence = estimate_confidence(assistant_chunks[-3:] or assistant_chunks, success)
            quality = estimate_quality(success, failure_signals, len(assistant_messages), last_assistant_text)

            runs.append(
                normalize_run(
                    run_id=raw.get("key", session_path.stem),
                    task=short_text(first_user.get("content") or last_assistant_text),
                    started_at=started_at,
                    duration_ms=duration_ms,
                    success=success,
                    tool_calls=tool_calls,
                    tool_errors=failure_signals,
                    retries=retries,
                    context_tokens=context_tokens,
                    output_quality=quality,
                    adherence=adherence,
                    confidence=confidence,
                    notes=build_notes(success, failure_signals, retries, context_tokens),
                )
            )

        return AdapterLoadResult(
            adapter_id=self.adapter_id,
            label=self.label,
            agent_name="seju-lite",
            runs=runs,
            source_path=self._as_string(self.sessions_dir),
            warnings=warnings,
        )

from __future__ import annotations

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


class NanobotAdapter(RuntimeAdapter):
    adapter_id = "nanobot"
    label = "nanobot"

    def __init__(self, workspace_root: Path | None = None, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(r"d:\ProjectsCollection\nanobot")
        self.workspace_root = workspace_root or Path.home() / ".nanobot" / "workspace"
        self.sessions_dir = self.workspace_root / "sessions"

    def describe(self) -> AdapterDescriptor:
        if self.sessions_dir.exists():
            session_files = list(self.sessions_dir.glob("*.jsonl"))
            return AdapterDescriptor(
                adapter_id=self.adapter_id,
                label=self.label,
                status="ready" if session_files else "empty",
                message=f"Detected {len(session_files)} nanobot session file(s).",
                source_path=self._as_string(self.sessions_dir),
            )

        return AdapterDescriptor(
            adapter_id=self.adapter_id,
            label=self.label,
            status="missing",
            message="No local nanobot workspace was found. Adapter scaffold is ready for ~/.nanobot/workspace/sessions.",
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
                agent_name="nanobot",
                runs=[],
                source_path=descriptor.source_path,
                warnings=warnings,
            )

        runs = []
        for session_path in sorted_paths(list(self.sessions_dir.glob("*.jsonl")))[:rolling_window]:
            try:
                lines = [line.strip() for line in session_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                raw_items = [json.loads(line) for line in lines]
            except Exception as exc:
                warnings.append(f"Failed to parse {session_path.name}: {exc}")
                continue

            metadata = next((item for item in raw_items if item.get("_type") == "metadata"), {})
            messages = [item for item in raw_items if item.get("_type") != "metadata"]
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

            started_dt = parse_timestamp(first_user.get("timestamp")) or parse_timestamp(metadata.get("created_at"))
            ended_dt = parse_timestamp(metadata.get("updated_at")) or (
                parse_timestamp(messages[-1].get("timestamp")) if messages else None
            )
            started_at = (started_dt or ended_dt).isoformat() if (started_dt or ended_dt) else session_path.name
            duration_ms = derive_duration_ms(started_dt, ended_dt, len(messages))
            context_tokens = estimate_context_tokens(text_chunks)
            adherence = estimate_adherence(last_assistant_text, failure_signals, success)
            confidence = estimate_confidence(assistant_chunks[-3:] or assistant_chunks, success)
            quality = estimate_quality(success, failure_signals, len(assistant_messages), last_assistant_text)

            runs.append(
                normalize_run(
                    run_id=metadata.get("key", session_path.stem),
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
            agent_name="nanobot",
            runs=runs,
            source_path=self._as_string(self.sessions_dir),
            warnings=warnings,
        )

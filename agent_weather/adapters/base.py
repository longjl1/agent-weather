from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from agent_weather.models import AgentRun


@dataclass
class AdapterDescriptor:
    adapter_id: str
    label: str
    status: str
    message: str
    source_path: str | None = None


@dataclass
class AdapterLoadResult:
    adapter_id: str
    label: str
    agent_name: str
    runs: list[AgentRun]
    source_path: str | None = None
    warnings: list[str] = field(default_factory=list)


class RuntimeAdapter(ABC):
    adapter_id: str
    label: str

    @abstractmethod
    def describe(self) -> AdapterDescriptor:
        raise NotImplementedError

    @abstractmethod
    def load_runs(self, rolling_window: int) -> AdapterLoadResult:
        raise NotImplementedError

    @staticmethod
    def _as_string(path: Path | None) -> str | None:
        return str(path) if path else None

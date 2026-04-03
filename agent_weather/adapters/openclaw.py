from __future__ import annotations

from pathlib import Path

from agent_weather.adapters.base import AdapterDescriptor, AdapterLoadResult, RuntimeAdapter


class OpenClawAdapter(RuntimeAdapter):
    adapter_id = "openclaw"
    label = "openclaw"

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path(r"d:\ProjectsCollection\openclaw")

    def describe(self) -> AdapterDescriptor:
        if self.project_root.exists():
            return AdapterDescriptor(
                adapter_id=self.adapter_id,
                label=self.label,
                status="stub",
                message="Project found, but runtime extraction rules are still scaffold-only.",
                source_path=self._as_string(self.project_root),
            )

        return AdapterDescriptor(
            adapter_id=self.adapter_id,
            label=self.label,
            status="missing",
            message="Project directory not found. Adapter scaffold is ready for future integration.",
            source_path=self._as_string(self.project_root),
        )

    def load_runs(self, rolling_window: int) -> AdapterLoadResult:
        descriptor = self.describe()
        return AdapterLoadResult(
            adapter_id=self.adapter_id,
            label=self.label,
            agent_name="openclaw",
            runs=[],
            source_path=descriptor.source_path,
            warnings=[descriptor.message],
        )

from __future__ import annotations

from agent_weather.adapters.base import AdapterDescriptor, AdapterLoadResult, RuntimeAdapter
from agent_weather.data.mock_runs import load_mock_runs


class MockRuntimeAdapter(RuntimeAdapter):
    adapter_id = "mock"
    label = "Mock runtime"

    def describe(self) -> AdapterDescriptor:
        return AdapterDescriptor(
            adapter_id=self.adapter_id,
            label=self.label,
            status="ready",
            message="Built-in mock runs for layout and evaluation testing.",
        )

    def load_runs(self, rolling_window: int) -> AdapterLoadResult:
        runs = load_mock_runs()[:rolling_window]
        return AdapterLoadResult(
            adapter_id=self.adapter_id,
            label=self.label,
            agent_name="demo-agent",
            runs=runs,
            source_path=None,
        )

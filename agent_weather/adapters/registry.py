from __future__ import annotations

from agent_weather.adapters.base import RuntimeAdapter
from agent_weather.adapters.mock import MockRuntimeAdapter
from agent_weather.adapters.nanobot import NanobotAdapter
from agent_weather.adapters.openclaw import OpenClawAdapter
from agent_weather.adapters.seju_lite import SejuLiteAdapter


def build_adapter_registry() -> dict[str, RuntimeAdapter]:
    adapters: list[RuntimeAdapter] = [
        SejuLiteAdapter(),
        NanobotAdapter(),
        OpenClawAdapter(),
        MockRuntimeAdapter(),
    ]
    return {adapter.adapter_id: adapter for adapter in adapters}

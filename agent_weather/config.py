from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_title: str = "Agent Weather"
    agent_name: str = "seju-lite / primary-agent"
    rolling_window: int = 10
    enable_llm_evaluator: bool = False


DEFAULT_CONFIG = AppConfig()

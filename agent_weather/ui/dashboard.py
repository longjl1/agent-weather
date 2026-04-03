import json

import streamlit as st

from agent_weather.adapters import build_adapter_registry
from agent_weather.config import DEFAULT_CONFIG
from agent_weather.services.aggregator import aggregate_runs
from agent_weather.services.context_builder import build_evaluation_context
from agent_weather.services.evaluator import run_placeholder_evaluator
from agent_weather.services.weather_rules import classify_weather
from agent_weather.ui.sections import (
    apply_run_filter,
    inject_console_css,
    render_evaluator_panel,
    render_future_modules,
    render_header,
    render_health_summary,
    render_operator_panel,
    render_recent_runs,
    render_sidebar_navigation,
    render_skills_panel,
    render_source_status,
    render_state_evidence,
    render_trend_summary,
    render_weather_hero,
)


def render_dashboard() -> None:
    st.set_page_config(
        page_title=DEFAULT_CONFIG.app_title,
        page_icon="\U0001f326\ufe0f",
        layout="wide",
    )

    inject_console_css()
    adapter_registry = build_adapter_registry()
    descriptors = {adapter_id: adapter.describe() for adapter_id, adapter in adapter_registry.items()}

    if "aw_adapter_id" not in st.session_state:
        preferred = next(
            (adapter_id for adapter_id, descriptor in descriptors.items() if descriptor.status == "ready"),
            "mock",
        )
        st.session_state["aw_adapter_id"] = preferred

    current_page = st.session_state.get("aw_page", "Overview")
    current_adapter_id = st.session_state["aw_adapter_id"]
    page, adapter_id = render_sidebar_navigation(descriptors, current_adapter_id, current_page)
    adapter = adapter_registry.get(adapter_id, adapter_registry["mock"])
    load_result = adapter.load_runs(DEFAULT_CONFIG.rolling_window)

    render_header(load_result.agent_name or DEFAULT_CONFIG.agent_name)

    runs = load_result.runs[: DEFAULT_CONFIG.rolling_window]
    run_filter = st.session_state.get("aw_run_filter", "All runs")
    filtered_runs = apply_run_filter(runs, run_filter)
    effective_runs = filtered_runs or runs

    metrics = aggregate_runs(effective_runs)
    weather = classify_weather(metrics)
    runtime_config = DEFAULT_CONFIG.__class__(
        app_title=DEFAULT_CONFIG.app_title,
        agent_name=load_result.agent_name,
        rolling_window=DEFAULT_CONFIG.rolling_window,
        enable_llm_evaluator=DEFAULT_CONFIG.enable_llm_evaluator,
    )
    context = build_evaluation_context(effective_runs, metrics, runtime_config)
    evaluator_output = run_placeholder_evaluator(context, weather)

    st.markdown("")

    if page == "Overview":
        render_weather_hero(weather)
        render_health_summary(metrics)

        st.markdown("")
        center_left, center_right = st.columns([1.35, 1], gap="large")

        with center_left:
            render_state_evidence(weather)

        with center_right:
            st.markdown("#### Why This Weather")
            st.markdown(
                """
                <div class="aw-panel-soft">
                    <div class="aw-mini-note">
                        The current weather state is based on recent success rate, tool error pressure,
                        retry behavior, adherence stability, and confidence. The center view only shows the current climate,
                        its causes, and the most important next move.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_evaluator_panel(evaluator_output)

        st.markdown("")
        lower_left, lower_right = st.columns([1.02, 1.25], gap="large")

        with lower_left:
            render_source_status(load_result, descriptors[adapter_id])
            st.markdown("")
            render_trend_summary(effective_runs)

        with lower_right:
            render_skills_panel(weather)

    elif page == "Evidence":
        left, right = st.columns([1.15, 1], gap="large")
        with left:
            render_recent_runs(effective_runs)
        with right:
            render_source_status(load_result, descriptors[adapter_id])
            st.markdown("")
            render_trend_summary(effective_runs)
            st.markdown("")
            if st.session_state.get("aw_show_debug", False):
                st.markdown("#### Debug Context")
                st.code(json.dumps(context.__dict__, ensure_ascii=False, indent=2), language="json")
            else:
                st.markdown("#### Operating Notes")
                st.markdown(
                    """
                    <div class="aw-panel-soft">
                        <div class="aw-mini-note">
                            Evidence view is for session-level inspection, run-by-run review, and runtime source inspection.
                            Keep this page open when tuning thresholds or validating a new adapter.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    elif page == "Interventions":
        left, right = st.columns([1, 1.2], gap="large")
        with left:
            render_skills_panel(weather)
        with right:
            render_evaluator_panel(evaluator_output)
            st.markdown("")
            render_operator_panel()

    elif page == "Extensions":
        render_source_status(load_result, descriptors[adapter_id])
        st.markdown("")
        render_future_modules(context)

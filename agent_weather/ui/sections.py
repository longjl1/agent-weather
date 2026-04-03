from __future__ import annotations

import statistics

import streamlit as st

from agent_weather.adapters.base import AdapterDescriptor, AdapterLoadResult
from agent_weather.models import AgentRun, AggregateMetrics, EvaluationContext, WeatherReport


WEATHER_META = {
    "sunny": {
        "icon": "\u2600\ufe0f",
        "tone": "Stable and reliable",
        "chip": "Healthy",
    },
    "cloudy": {
        "icon": "\u26c5",
        "tone": "Operational but uncertain",
        "chip": "Watch",
    },
    "windy": {
        "icon": "\U0001f32c\ufe0f",
        "tone": "Context drift detected",
        "chip": "Drift",
    },
    "rainy": {
        "icon": "\U0001f327\ufe0f",
        "tone": "Execution friction increasing",
        "chip": "Degraded",
    },
    "storm": {
        "icon": "\u26c8\ufe0f",
        "tone": "High operator risk",
        "chip": "Critical",
    },
    "fog": {
        "icon": "\U0001f32b\ufe0f",
        "tone": "Low confidence / weak explainability",
        "chip": "Opaque",
    },
    "aurora": {
        "icon": "\U0001f30c",
        "tone": "Exceptionally strong performance",
        "chip": "Peak",
    },
}


def inject_console_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top, rgba(160, 186, 210, 0.08), transparent 26%),
                linear-gradient(180deg, #0d1116 0%, #10151b 55%, #0c1015 100%);
            color: #e9edf2;
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }

        .aw-panel {
            background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.025));
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
        }

        .aw-panel-soft {
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 18px;
            padding: 0.9rem 1rem;
        }

        .aw-hero {
            background:
                radial-gradient(circle at top, rgba(178, 199, 225, 0.12), transparent 28%),
                linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 30px;
            padding: 1.35rem 1.35rem 1.15rem;
            box-shadow: 0 28px 80px rgba(0, 0, 0, 0.22);
        }

        .aw-kicker {
            text-transform: uppercase;
            letter-spacing: 0.18em;
            font-size: 0.72rem;
            color: rgba(233, 237, 242, 0.48);
            margin-bottom: 0.45rem;
        }

        .aw-title {
            font-size: 3.2rem;
            line-height: 0.95;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin: 0;
        }

        .aw-subtitle {
            color: rgba(233, 237, 242, 0.66);
            font-size: 1rem;
            line-height: 1.65;
            margin-top: 0.8rem;
            margin-bottom: 0;
            max-width: 60rem;
        }

        .aw-weather-row {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1.25rem;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .aw-weather-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            border: 1px solid rgba(255,255,255,0.09);
            border-radius: 999px;
            padding: 0.5rem 0.8rem;
            background: rgba(255,255,255,0.04);
            font-size: 0.84rem;
            color: rgba(233, 237, 242, 0.78);
        }

        .aw-weather-icon {
            font-size: 3rem;
            line-height: 1;
        }

        .aw-weather-label {
            font-size: 2.25rem;
            line-height: 1;
            font-weight: 700;
            letter-spacing: -0.04em;
            margin: 0.2rem 0 0 0;
        }

        .aw-health {
            text-align: right;
            min-width: 180px;
        }

        .aw-health-label {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.7rem;
            color: rgba(233, 237, 242, 0.46);
        }

        .aw-health-score {
            font-size: 3rem;
            line-height: 1;
            font-weight: 700;
            margin: 0.35rem 0 0 0;
        }

        .aw-chip {
            display: inline-block;
            margin-top: 0.55rem;
            padding: 0.32rem 0.58rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.045);
            color: rgba(233, 237, 242, 0.82);
            font-size: 0.74rem;
        }

        .aw-list {
            margin: 0;
            padding-left: 1rem;
            color: rgba(233, 237, 242, 0.8);
            line-height: 1.7;
        }

        .aw-empty {
            border: 1px dashed rgba(255,255,255,0.12);
            border-radius: 18px;
            padding: 1rem;
            color: rgba(233, 237, 242, 0.58);
            background: rgba(255,255,255,0.02);
        }

        .aw-mini-note {
            color: rgba(233, 237, 242, 0.56);
            font-size: 0.85rem;
            line-height: 1.65;
        }

        div[data-testid="stExpander"] > details {
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 18px;
            background: rgba(255,255,255,0.025);
        }

        section[data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)),
                #0b0f14;
            border-right: 1px solid rgba(255,255,255,0.07);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(agent_name: str) -> None:
    st.markdown(
        f"""
        <div class="aw-panel">
            <div class="aw-kicker">Agent Observability Console</div>
            <h1 class="aw-title">Agent Weather</h1>
            <p class="aw-subtitle">
                A compact operating climate for <strong>{agent_name}</strong>.
                Read the current weather, understand what caused it, and identify the next best intervention.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(
    descriptors: dict[str, AdapterDescriptor],
    current_adapter_id: str,
    current_page: str,
) -> tuple[str, str]:
    with st.sidebar:
        st.markdown("### Agent Weather")
        st.caption("Small control room for runtime health, diagnosis, and intervention.")
        page = st.radio(
            "Console View",
            options=["Overview", "Evidence", "Interventions", "Extensions"],
            index=["Overview", "Evidence", "Interventions", "Extensions"].index(current_page),
            key="aw_page",
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown("#### Runtime")
        adapter_ids = list(descriptors.keys())
        selected_index = adapter_ids.index(current_adapter_id) if current_adapter_id in adapter_ids else 0
        adapter_id = st.selectbox(
            "Runtime Adapter",
            options=adapter_ids,
            index=selected_index,
            format_func=lambda adapter: f"{descriptors[adapter].label} [{descriptors[adapter].status}]",
            key="aw_adapter_id",
        )

        st.markdown("#### Session Window")
        st.session_state["aw_run_filter"] = st.selectbox(
            "Run Filter",
            ["All runs", "Successful only", "Failed only"],
            index=["All runs", "Successful only", "Failed only"].index(
                st.session_state.get("aw_run_filter", "All runs")
            ),
        )

        st.session_state["aw_show_evaluator"] = st.toggle(
            "Show evaluator raw output",
            value=st.session_state.get("aw_show_evaluator", True),
        )
        st.session_state["aw_show_memory"] = st.toggle(
            "Show future memory module",
            value=st.session_state.get("aw_show_memory", True),
        )
        st.session_state["aw_show_debug"] = st.toggle(
            "Show debug context",
            value=st.session_state.get("aw_show_debug", False),
        )

        st.divider()
        st.markdown("#### Thresholds")
        st.slider("Success", 0.0, 1.0, st.session_state.get("aw_threshold_success", 0.70), 0.05, key="aw_threshold_success")
        st.slider(
            "Tool error",
            0.0,
            0.5,
            st.session_state.get("aw_threshold_tool_error", 0.18),
            0.01,
            key="aw_threshold_tool_error",
        )
        st.slider("Retries", 0.0, 5.0, st.session_state.get("aw_threshold_retry", 2.0), 0.5, key="aw_threshold_retry")
        st.slider(
            "Confidence",
            0.0,
            1.0,
            st.session_state.get("aw_threshold_confidence", 0.60),
            0.05,
            key="aw_threshold_confidence",
        )

        if st.button("Refresh Evaluation", type="primary", use_container_width=True):
            st.session_state["aw_refresh_count"] = st.session_state.get("aw_refresh_count", 0) + 1

        with st.expander("Advanced Debug Controls", expanded=False):
            st.caption("Reserved for runtime source switching, trace replay toggles, and evaluator overrides.")
            st.text_input("Evaluator profile", value="single-agent-reviewer")
            st.text_input("Trace source", value="mock://recent-runs")

    return page, adapter_id


def render_source_status(load_result: AdapterLoadResult, descriptor: AdapterDescriptor) -> None:
    st.markdown("#### Runtime Source")
    st.markdown(
        f"""
        <div class="aw-panel-soft">
            <div class="aw-kicker">Current Adapter</div>
            <div style="font-size:1.05rem; font-weight:600; margin-bottom:0.4rem;">{load_result.label}</div>
            <div class="aw-mini-note">{descriptor.message}</div>
            <div class="aw-mini-note" style="margin-top:0.5rem;">Source path: <strong>{descriptor.source_path or "built-in"}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for warning in load_result.warnings:
        st.warning(warning)


def render_weather_hero(report: WeatherReport) -> None:
    meta = WEATHER_META.get(report.weather, WEATHER_META["cloudy"])
    health_score = int(report.score * 100)

    st.markdown(
        f"""
        <div class="aw-hero">
            <div class="aw-kicker">Current Operating Climate</div>
            <div class="aw-weather-row">
                <div>
                    <div class="aw-weather-badge">{meta["icon"]} {meta["tone"]}</div>
                    <div style="display:flex; align-items:center; gap:0.95rem; margin-top:0.9rem;">
                        <div class="aw-weather-icon">{meta["icon"]}</div>
                        <div>
                            <p class="aw-weather-label">{report.weather.title()}</p>
                            <p class="aw-subtitle" style="margin-top:0.45rem; max-width:44rem;">
                                {report.summary}
                            </p>
                        </div>
                    </div>
                </div>
                <div class="aw-health">
                    <div class="aw-health-label">Overall Health</div>
                    <div class="aw-health-score">{health_score}</div>
                    <div class="aw-chip">{meta["chip"]}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_health_summary(metrics: AggregateMetrics) -> None:
    st.markdown('<div class="aw-kicker" style="margin-top:0.8rem;">Status Summary</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Success Rate", f"{metrics.success_rate:.0%}")
    cols[1].metric("Tool Error Rate", f"{metrics.tool_error_rate:.0%}")
    cols[2].metric("Avg Retries", f"{metrics.avg_retries:.2f}")
    cols[3].metric("Avg Confidence", f"{metrics.avg_confidence:.2f}")


def render_state_evidence(report: WeatherReport) -> None:
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="aw-panel-soft">', unsafe_allow_html=True)
        st.markdown("#### Risk Factors")
        risks = report.risks or ["No major risks detected in the current window."]
        st.markdown(
            "<ul class='aw-list'>" + "".join(f"<li>{item}</li>" for item in risks) + "</ul>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="aw-panel-soft">', unsafe_allow_html=True)
        st.markdown("#### Strengths")
        strengths = report.strengths or ["No strong positive signals detected yet."]
        st.markdown(
            "<ul class='aw-list'>" + "".join(f"<li>{item}</li>" for item in strengths) + "</ul>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_trend_summary(runs: list[AgentRun]) -> None:
    st.markdown("#### Trend Summary")
    if not runs:
        st.info("No recent runs available.")
        return

    recent_success = "".join("●" if run.success else "○" for run in runs)
    quality_values = [run.output_quality for run in runs]
    confidence_values = [run.confidence for run in runs]
    avg_quality = statistics.mean(quality_values)
    avg_confidence = statistics.mean(confidence_values)

    col_a, col_b = st.columns([1.3, 1], gap="large")
    with col_a:
        st.markdown(
            f"""
            <div class="aw-panel-soft">
                <div class="aw-kicker">Recent Pattern</div>
                <div style="font-size:1.2rem; letter-spacing:0.3em; margin-bottom:0.5rem;">{recent_success}</div>
                <div class="aw-mini-note">
                    Filled markers indicate successful runs. Empty markers indicate failed runs in the current window.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f"""
            <div class="aw-panel-soft">
                <div class="aw-kicker">Current Averages</div>
                <div class="aw-mini-note">Quality: <strong>{avg_quality:.2f}</strong></div>
                <div class="aw-mini-note">Confidence: <strong>{avg_confidence:.2f}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_recent_runs(runs: list[AgentRun]) -> None:
    st.markdown("#### Recent Runs")
    if not runs:
        st.info("No runs available for the selected adapter.")
        return
    rows = []
    for run in runs:
        rows.append(
            {
                "run": run.id,
                "task": run.task,
                "success": "yes" if run.success else "no",
                "duration_ms": run.duration_ms,
                "tool_errors": run.tool_errors,
                "retries": run.retries,
                "context_tokens": run.context_tokens,
                "quality": f"{run.output_quality:.2f}",
                "adherence": f"{run.adherence:.2f}",
                "confidence": f"{run.confidence:.2f}",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

def render_operator_panel() -> None:
    st.markdown("### Operator Controls")
    with st.expander("Console Controls", expanded=False):
        st.caption("Primary controls have moved into the sidebar to keep the main console quieter.")
        st.write(f"- Runtime adapter: `{st.session_state.get('aw_adapter_id', 'mock')}`")
        st.write(f"- Run filter: `{st.session_state.get('aw_run_filter', 'All runs')}`")
        st.write(f"- Success threshold: `{st.session_state.get('aw_threshold_success', 0.70):.2f}`")
        st.write(f"- Tool error threshold: `{st.session_state.get('aw_threshold_tool_error', 0.18):.2f}`")
        st.write(f"- Retry threshold: `{st.session_state.get('aw_threshold_retry', 2.0):.1f}`")
        st.write(f"- Confidence threshold: `{st.session_state.get('aw_threshold_confidence', 0.60):.2f}`")
        st.info("Use the sidebar to change controls, data sources, and debug visibility.")


def render_skills_panel(report: WeatherReport) -> None:
    st.markdown("### Recommended Interventions")
    if not report.suggestions:
        st.markdown('<div class="aw-empty">No skill recommendations right now.</div>', unsafe_allow_html=True)
        return

    for index, suggestion in enumerate(report.suggestions, start=1):
        priority = "High" if index == 1 else "Medium"
        with st.expander(f"{suggestion.title}  |  {priority} priority", expanded=index == 1):
            st.write(suggestion.reason)
            if suggestion.prompt_patch:
                st.caption("Prompt patch")
                st.code(suggestion.prompt_patch, language="text")
            if suggestion.system_patch:
                st.caption("System patch")
                st.code(suggestion.system_patch, language="text")


def render_evaluator_panel(evaluator_output: dict) -> None:
    st.markdown("### Evaluator Diagnosis")
    st.markdown(
        '<div class="aw-mini-note">LLM-facing diagnosis stays secondary to the deterministic weather state, but it should explain and sharpen the operator\'s next move.</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("aw_show_evaluator", True):
        with st.expander("Raw evaluator output", expanded=False):
            st.json(evaluator_output)
        with st.expander("Prompt preview", expanded=False):
            st.code(evaluator_output["prompt_preview"], language="text")


def render_future_modules(context: EvaluationContext) -> None:
    st.markdown("### Future Extensions")
    tabs = st.tabs(["Memory Module", "Trace Replay", "Incidents", "Patch Compare", "Evaluator Context"])

    with tabs[0]:
        st.markdown(
            '<div class="aw-empty">Reserved for agent memory snapshots, memory drift monitoring, and memory-linked weather changes.</div>',
            unsafe_allow_html=True,
        )

    with tabs[1]:
        st.markdown(
            '<div class="aw-empty">Reserved for trace playback, run step replay, and tool-by-tool incident review.</div>',
            unsafe_allow_html=True,
        )

    with tabs[2]:
        st.markdown(
            '<div class="aw-empty">Reserved for incident history, repeated failure clusters, and operator annotations.</div>',
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown(
            '<div class="aw-empty">Reserved for before/after prompt patch comparison and weather deltas.</div>',
            unsafe_allow_html=True,
        )

    with tabs[4]:
        st.code(str(context.__dict__), language="python")


def apply_run_filter(runs: list[AgentRun], run_filter: str) -> list[AgentRun]:
    if run_filter == "Successful only":
        return [run for run in runs if run.success]
    if run_filter == "Failed only":
        return [run for run in runs if not run.success]
    return runs

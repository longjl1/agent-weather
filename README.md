# Agent Weather

`Agent Weather` is a Streamlit-based observability console for a single AI agent.

Instead of showing only raw logs or pass/fail metrics, it summarizes the current operating condition of the agent as a weather system:

- `Sunny`: stable, reliable, low-friction runs
- `Cloudy`: acceptable outputs with rising uncertainty
- `Windy`: context drift, scope instability, or instruction loss
- `Rainy`: retries, tool failures, and degraded execution quality
- `Storm`: severe instability, repeated failures, or high operator risk
- `Fog`: superficially okay outputs with low confidence or poor explainability
- `Aurora`: unusually strong, resilient, or high-quality performance

The goal is to give operators a fast answer to one question:

**"How healthy is this agent right now, and what should we improve next?"**

## Product Direction

This project is not a generic admin dashboard.

It is a lightweight control surface for:

- monitoring a single agent over recent runs
- summarizing behavior into a human-readable weather metaphor
- packaging current performance into evaluation context
- sending that context to an LLM evaluator
- returning operational suggestions and recommended skills

## Core Idea

The system combines two layers:

1. Rule-based weather classification
   Use deterministic heuristics to assign a stable baseline weather state from runtime signals.

2. LLM-based diagnosis
   Feed a structured run summary to an evaluator model that explains the weather, identifies risks, and suggests improvements.

This hybrid design keeps the weather stable and interpretable while still allowing higher-level reasoning and suggestions.

## MVP Scope

Version 1 should stay intentionally small.

### Included

- Streamlit single-page console
- mock agent runs
- deterministic weather scoring
- LLM evaluation prompt scaffold
- recommended skills panel
- run trend summary
- operator-friendly explanation layer

### Not Included Yet

- real runtime integration
- multi-agent support
- persistent storage
- authentication
- automatic patch application
- full trace replay

## User Flow

1. Load recent agent runs
2. Aggregate key metrics
3. Compute baseline weather from rules
4. Build structured evaluation context
5. Send context to LLM evaluator
6. Render:
   - current weather
   - score
   - risk factors
   - strengths
   - recommended skills
   - recent run table

## Example Runtime Signals

The first version can use a compact run schema like this:

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentRun:
    id: str
    task: str
    started_at: str
    duration_ms: int
    success: bool
    tool_calls: int
    tool_errors: int
    retries: int
    context_tokens: int
    output_quality: float
    adherence: float
    confidence: float
    notes: Optional[str] = None
```

## Example Weather Mapping

Initial rules can be simple:

- low success + high tool errors -> `storm`
- medium success + many retries -> `rainy`
- good success + low confidence -> `fog`
- high context + weak adherence -> `windy`
- strong consistency + good quality -> `sunny`
- exceptional recovery + strong quality -> `aurora`

## Suggested Skill Types

The suggestions panel should not be abstract. It should recommend small operational interventions such as:

- `Context Compression`
- `Instruction Adherence Patch`
- `Tool Retry Guard`
- `Failure Recovery Loop`
- `Output Formatter`
- `Scope Narrowing`
- `Self-Check Before Final`
- `Uncertainty Disclosure`

Each suggestion should explain:

- why it is recommended
- what issue it addresses
- an example prompt or system patch

## Architecture

```text
agent-weather/
├─ app.py
├─ README.md
├─ pyproject.toml
└─ agent_weather/
   ├─ __init__.py
   ├─ models.py
   ├─ config.py
   ├─ data/
   │  └─ mock_runs.py
   ├─ services/
   │  ├─ aggregator.py
   │  ├─ weather_rules.py
   │  ├─ evaluator.py
   │  ├─ skill_suggestions.py
   │  └─ context_builder.py
   └─ ui/
      ├─ dashboard.py
      └─ sections.py
```

## Project Plan

### V1

- build Streamlit console
- use mock run data
- implement baseline weather rules
- display LLM evaluator placeholder output
- render skills suggestions

### V2

- connect to real agent trace/log files
- compute rolling weather over last N runs
- add trend chart and incident history
- compare operator notes vs agent health

### V3

- generate prompt patches automatically
- allow "apply recommendation" workflows
- feed updated patches back into runtime
- compare before/after weather impact

## Development Notes

- keep the UI closer to an operations console than a SaaS dashboard
- make weather the primary visual metaphor
- use a small number of strong panels
- keep all evaluator outputs structured
- prefer deterministic metrics for core state and LLMs for explanation

## Quick Start

```bash
cd agent-weather
uv venv
.venv\Scripts\activate
uv pip install -e .
streamlit run app.py
```

## Next Step

The immediate next implementation milestone is:

**finish a fully working V1 that uses mock runs, deterministic weather rules, and a placeholder evaluator response rendered in Streamlit.**

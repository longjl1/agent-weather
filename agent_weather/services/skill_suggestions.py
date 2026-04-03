from agent_weather.models import AggregateMetrics, SkillSuggestion


def suggest_skills(metrics: AggregateMetrics) -> list[SkillSuggestion]:
    suggestions: list[SkillSuggestion] = []

    if metrics.avg_context_tokens > 12000:
        suggestions.append(
            SkillSuggestion(
                title="Context Compression",
                reason="The agent accumulates too much context and may lose task focus on longer runs.",
                prompt_patch="Before each major step, summarize current goals and discard irrelevant details.",
                system_patch="If context exceeds threshold, create a compressed task state before proceeding.",
            )
        )

    if metrics.avg_adherence < 0.8:
        suggestions.append(
            SkillSuggestion(
                title="Instruction Adherence Patch",
                reason="The agent shows signs of drifting from requested structure or formatting.",
                prompt_patch="Before finalizing, compare your draft against the user's explicit formatting requirements.",
                system_patch="Run a final instruction-compliance checklist before the final answer.",
            )
        )

    if metrics.tool_error_rate > 0.2 or metrics.avg_retries > 2:
        suggestions.append(
            SkillSuggestion(
                title="Tool Retry Guard",
                reason="Tool instability and retries are degrading runtime reliability.",
                prompt_patch="After each tool failure, decide whether retrying is justified or whether a fallback path is better.",
                system_patch="Cap repeated retries and escalate to fallback reasoning earlier.",
            )
        )

    if metrics.avg_confidence < 0.6:
        suggestions.append(
            SkillSuggestion(
                title="Uncertainty Disclosure",
                reason="The agent often operates with low confidence and should surface uncertainty more clearly.",
                prompt_patch="When confidence is low, explicitly say what is uncertain and what should be verified.",
            )
        )

    return suggestions

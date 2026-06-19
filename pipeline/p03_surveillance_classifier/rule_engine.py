"""Deterministic rule engine for IJOP-like surveillance scoring."""

from typing import Any

from pipeline.common.config import load_classifier_rules
from pipeline.p01_persona_extraction.schema import PersonaProfile


def _match_trigger(profile: PersonaProfile, trigger: dict[str, Any]) -> bool:
    attr = trigger["attribute"]
    value = getattr(profile, attr, None)

    if "value" in trigger:
        return value == trigger["value"]
    if "values" in trigger:
        return value in trigger["values"]
    if "threshold" in trigger:
        return (value or 0) >= trigger["threshold"]
    return False


def _category_for_score(score: float, thresholds: dict[str, float]) -> str:
    if score >= thresholds.get("flagged", 80):
        return "flagged"
    if score >= thresholds.get("high", 60):
        return "high"
    if score >= thresholds.get("medium", 30):
        return "medium"
    return "low"


def score_profile(profile: PersonaProfile, rules: dict | None = None) -> PersonaProfile:
    rules = rules or load_classifier_rules()
    triggered: list[str] = []
    score = 0.0

    for group in ("critical_triggers", "medium_triggers", "network_triggers"):
        for trigger in rules.get("risk_rules", {}).get(group, []):
            if _match_trigger(profile, trigger):
                score += trigger.get("weight", 0)
                triggered.append(f"{group}:{trigger['attribute']}")

    thresholds = rules.get("thresholds", {})
    return profile.model_copy(
        update={
            "risk_score": min(score, 100.0),
            "risk_category": _category_for_score(score, thresholds),
            "association_rules_triggered": triggered or None,
        }
    )


def score_profiles(profiles: list[PersonaProfile]) -> list[PersonaProfile]:
    return [score_profile(p) for p in profiles]

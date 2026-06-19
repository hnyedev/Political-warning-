"""Deterministic classifier agent applying rule engine + association rules."""

from dataclasses import dataclass

from pipeline.p03_surveillance_classifier.rule_engine import score_profile
from pipeline.p04_camel_agents.citizen_agent import SimulatedAction
from pipeline.p01_persona_extraction.schema import PersonaProfile


@dataclass
class ClassificationDecision:
    persona_id: str
    risk_score: float
    risk_category: str
    rules_triggered: list[str]
    recommended_action: str


class ClassifierAgent:
    def classify(
        self,
        profile: PersonaProfile,
        actions: list[SimulatedAction],
    ) -> ClassificationDecision:
        scored = score_profile(profile)
        action = "monitor"
        if scored.risk_category == "flagged":
            action = "flag"
        elif scored.risk_category == "high":
            action = "interrogate"

        return ClassificationDecision(
            persona_id=profile.persona_id,
            risk_score=scored.risk_score or 0.0,
            risk_category=scored.risk_category or "low",
            rules_triggered=scored.association_rules_triggered or [],
            recommended_action=action,
        )

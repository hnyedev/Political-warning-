"""Auditor agent: false positives, constitutional violations, chilling effect."""

from dataclasses import dataclass

from pipeline.common.config import load_classifier_rules
from pipeline.p04_camel_agents.classifier_agent import ClassificationDecision
from pipeline.p01_persona_extraction.schema import PersonaProfile


@dataclass
class AuditReport:
    persona_id: str
    is_false_positive: bool
    constitutional_violation: bool
    chilling_effect_detected: bool
    notes: str


class AuditorAgent:
    def audit(
        self,
        profile: PersonaProfile,
        decision: ClassificationDecision,
    ) -> AuditReport:
        rules = load_classifier_rules()
        protected = set(rules.get("protected_categories", []))
        is_protected = profile.political_activity in protected
        flagged = decision.risk_category == "flagged"

        return AuditReport(
            persona_id=profile.persona_id,
            is_false_positive=flagged and is_protected,
            constitutional_violation=flagged and is_protected,
            chilling_effect_detected=profile.chilling_effect_predicted or False,
            notes="Protected category flagged without threat indicators"
            if flagged and is_protected
            else "",
        )

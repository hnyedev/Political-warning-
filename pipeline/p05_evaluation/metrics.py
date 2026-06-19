"""Evaluation metrics for the surveillance simulation."""

from dataclasses import dataclass, asdict
import json
from pathlib import Path

from pipeline.common.config import load_classifier_rules
from pipeline.p03_surveillance_classifier.association_algorithms.risk_evaluator import (
    AlgorithmMetrics,
    from_runner_result,
)
from pipeline.p01_persona_extraction.schema import PersonaProfile


@dataclass
class EvaluationReport:
    total_population: int
    total_flagged: int
    flag_rate: float

    false_positive_rate: float
    protected_false_positive_rate: float
    recall_on_synthetic_threats: float

    whatsapp_bias_rate: float
    journalist_flag_rate: float

    apriori_metrics: AlgorithmMetrics
    fpgrowth_metrics: AlgorithmMetrics
    eclat_metrics: AlgorithmMetrics

    chilling_effect_index: float

    political_warning_triggered: bool
    political_warning_reason: str

    def to_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")


def _is_protected(profile: PersonaProfile, protected: set[str]) -> bool:
    return profile.political_activity in protected or profile.is_constitutionally_protected is True


def compute_evaluation_report(
    profiles: list[PersonaProfile],
    algorithm_results: dict,
    chilling_modified_count: int = 0,
) -> EvaluationReport:
    rules = load_classifier_rules()
    protected = set(rules.get("protected_categories", []))
    warning_cfg = rules.get("political_warning", {})

    total = len(profiles)
    flagged = [p for p in profiles if p.risk_category == "flagged"]
    protected_profiles = [p for p in profiles if _is_protected(p, protected)]
    protected_flagged = [p for p in flagged if _is_protected(p, protected)]

    encrypted_only = [
        p
        for p in flagged
        if p.uses_encrypted_apps
        and not p.uses_vpn
        and not p.uses_tor
        and p.political_activity not in {"journalist", "activist", "opposition"}
    ]
    journalists = [p for p in profiles if p.political_activity == "journalist"]
    journalist_flagged = [p for p in journalists if p.risk_category == "flagged"]

    protected_fpr = len(protected_flagged) / max(len(protected_profiles), 1)
    political_warning = protected_fpr > warning_cfg.get("protected_fpr_threshold", 0.15)
    reason = (
        f"Protected FPR {protected_fpr:.2%} exceeds threshold"
        if political_warning
        else "Within acceptable protected FPR bounds"
    )

    return EvaluationReport(
        total_population=total,
        total_flagged=len(flagged),
        flag_rate=len(flagged) / max(total, 1),
        false_positive_rate=len(protected_flagged) / max(len(flagged), 1),
        protected_false_positive_rate=protected_fpr,
        recall_on_synthetic_threats=0.0,
        whatsapp_bias_rate=len(encrypted_only) / max(total, 1),
        journalist_flag_rate=len(journalist_flagged) / max(len(journalists), 1),
        apriori_metrics=from_runner_result(algorithm_results.get("apriori", {})),
        fpgrowth_metrics=from_runner_result(algorithm_results.get("fp_growth", {})),
        eclat_metrics=from_runner_result(algorithm_results.get("eclat", {})),
        chilling_effect_index=chilling_modified_count / max(total, 1),
        political_warning_triggered=political_warning,
        political_warning_reason=reason,
    )

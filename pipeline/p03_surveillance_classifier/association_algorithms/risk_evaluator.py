"""Metrics for association-rule algorithms."""

from dataclasses import dataclass


@dataclass
class AlgorithmMetrics:
    rules_count: int
    protected_bias_score: float
    whatsapp_rule_count: int
    causal_plausibility: float
    runtime_seconds: float
    memory_mb: float


def from_runner_result(result: dict) -> AlgorithmMetrics:
    return AlgorithmMetrics(
        rules_count=result.get("rules_count", 0),
        protected_bias_score=result.get("protected_bias_score", 0.0),
        whatsapp_rule_count=result.get("whatsapp_rule_count", 0),
        causal_plausibility=0.0,
        runtime_seconds=result.get("runtime_seconds", 0.0),
        memory_mb=result.get("memory_mb", 0.0),
    )

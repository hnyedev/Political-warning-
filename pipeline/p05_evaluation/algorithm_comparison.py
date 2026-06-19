"""Compare Apriori, FP-Growth, and ECLAT association algorithms."""

from dataclasses import dataclass

from pipeline.p03_surveillance_classifier.association_algorithms.risk_evaluator import (
    AlgorithmMetrics,
)


@dataclass
class AlgorithmComparisonRow:
    algorithm: str
    metrics: AlgorithmMetrics
    bias_rank: int
    danger_assessment: str


def compare_algorithms(results: dict) -> list[AlgorithmComparisonRow]:
    rows: list[AlgorithmComparisonRow] = []
    ranked = sorted(
        results.items(),
        key=lambda item: item[1].get("protected_bias_score", 0),
        reverse=True,
    )

    for rank, (name, data) in enumerate(ranked, start=1):
        metrics = AlgorithmMetrics(
            rules_count=data.get("rules_count", 0),
            protected_bias_score=data.get("protected_bias_score", 0.0),
            whatsapp_rule_count=data.get("whatsapp_rule_count", 0),
            causal_plausibility=0.0,
            runtime_seconds=data.get("runtime_seconds", 0.0),
            memory_mb=data.get("memory_mb", 0.0),
        )
        rows.append(
            AlgorithmComparisonRow(
                algorithm=name,
                metrics=metrics,
                bias_rank=rank,
                danger_assessment="high" if rank == 1 else "moderate" if rank == 2 else "lower",
            )
        )
    return rows

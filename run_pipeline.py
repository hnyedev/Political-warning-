#!/usr/bin/env python3
"""Orchestrate the CAMEL-OASIS MX surveillance simulation pipeline."""

import argparse

from pipeline.common.paths import (
    EVALUATION_REPORT_PATH,
    PERSONAS_STRUCTURED_PATH,
    SOCIAL_GRAPH_PATH,
)
from pipeline.p01_persona_extraction.download_dataset import download_personas_sample
from pipeline.p02_graph_construction.centrality_scorer import profiles_from_graph, score_centralities
from pipeline.p02_graph_construction.social_graph_builder import build_social_graph, load_profiles
from pipeline.p03_surveillance_classifier.association_algorithms.runner import AssociationRiskAnalyzer
from pipeline.p03_surveillance_classifier.rule_engine import score_profiles
from pipeline.p04_camel_agents.auditor_agent import AuditorAgent
from pipeline.p04_camel_agents.citizen_agent import CitizenAgent
from pipeline.p04_camel_agents.classifier_agent import ClassifierAgent
from pipeline.p05_evaluation.metrics import compute_evaluation_report
from pipeline.p06_report.generate_report import generate_report


def run_agents(profiles: list) -> int:
    classifier = ClassifierAgent()
    auditor = AuditorAgent()
    chilling_count = 0

    for profile in profiles:
        citizen = CitizenAgent(profile, under_surveillance=True)
        actions = citizen.simulate()
        decision = classifier.classify(profile, actions)
        audit = auditor.audit(profile, decision)
        if audit.chilling_effect_detected or any(a.modified_due_to_surveillance for a in actions):
            chilling_count += 1

    return chilling_count


def run_pipeline(skip_download: bool = False) -> None:
    if not skip_download:
        download_personas_sample()

    profiles = load_profiles(PERSONAS_STRUCTURED_PATH) if PERSONAS_STRUCTURED_PATH.exists() else []
    if not profiles:
        raise FileNotFoundError(
            f"No structured personas at {PERSONAS_STRUCTURED_PATH}. "
            "Run phase 1 extraction first."
        )

    graph = build_social_graph(profiles)
    graph = score_centralities(graph)
    profiles = profiles_from_graph(graph)

    profiles = score_profiles(profiles)

    analyzer = AssociationRiskAnalyzer()
    algorithm_results = analyzer.compare_algorithms(profiles)

    chilling_count = run_agents(profiles)

    report = compute_evaluation_report(profiles, algorithm_results, chilling_count)
    report.to_json(EVALUATION_REPORT_PATH)
    generate_report()

    print(f"Graph exported to {SOCIAL_GRAPH_PATH}")
    print(f"Evaluation report: {EVALUATION_REPORT_PATH}")
    print(f"Political warning: {report.political_warning_triggered}")


def main() -> None:
    parser = argparse.ArgumentParser(description="CAMEL-OASIS MX surveillance pipeline")
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()
    run_pipeline(skip_download=args.skip_download)


if __name__ == "__main__":
    main()

"""Shared path constants for the surveillance simulation pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
GRAPH_DATA_DIR = DATA_DIR / "synthetic_graph"

CLASSIFIER_RULES_PATH = CONFIG_DIR / "classifier_rules.yaml"
ASSOCIATION_CONFIG_PATH = CONFIG_DIR / "association_config.yaml"

PERSONAS_SAMPLE_PATH = RAW_DATA_DIR / "personas_sample_10k.parquet"
PERSONAS_STRUCTURED_PATH = PROCESSED_DATA_DIR / "personas_structured.jsonl"
SOCIAL_GRAPH_PATH = GRAPH_DATA_DIR / "social_graph.graphml"
EVALUATION_REPORT_PATH = REPORTS_DIR / "evaluation_report.json"
TECHNICAL_REPORT_PATH = REPORTS_DIR / "technical_report.md"

SAMPLE_SIZE = 10_000
EXTRACTION_BATCH_SIZE = 50

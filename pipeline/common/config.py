"""YAML configuration loading utilities."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_classifier_rules() -> dict[str, Any]:
    from pipeline.common.paths import CLASSIFIER_RULES_PATH

    return load_yaml(CLASSIFIER_RULES_PATH)


def load_association_config() -> dict[str, Any]:
    from pipeline.common.paths import ASSOCIATION_CONFIG_PATH

    return load_yaml(ASSOCIATION_CONFIG_PATH)

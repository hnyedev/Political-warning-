"""Generate the technical Markdown report from evaluation results."""

import json
from pathlib import Path

from jinja2 import Template

from pipeline.common.paths import EVALUATION_REPORT_PATH, TECHNICAL_REPORT_PATH

REPORT_TEMPLATE = Template("""\
# CAMEL-OASIS MX Surveillance Simulation — Technical Report

## Executive Summary

1. **Flag rate:** {{ report.flag_rate | round(4) }} of the synthetic population was flagged.
2. **Protected FPR:** {{ report.protected_false_positive_rate | round(4) }} — primary political warning KPI.
3. **Political warning:** {{ "TRIGGERED" if report.political_warning_triggered else "Not triggered" }} — {{ report.political_warning_reason }}

## Methodology

Pipeline: PersonaHub extraction → social graph → rule engine + association mining → CAMEL agents → evaluation.

Sample size: {{ report.total_population }} synthetic personas (`latam-gpt/personas`).

## Classifier Results

| Metric | Value |
|---|---|
| Total flagged | {{ report.total_flagged }} |
| FPR (general) | {{ report.false_positive_rate | round(4) }} |
| Protected FPR | {{ report.protected_false_positive_rate | round(4) }} |
| WhatsApp bias rate | {{ report.whatsapp_bias_rate | round(4) }} |
| Journalist flag rate | {{ report.journalist_flag_rate | round(4) }} |
| Chilling effect index | {{ report.chilling_effect_index | round(4) }} |

## Association Algorithm Comparison

| Algorithm | Rules | Protected bias | WhatsApp rules | Runtime (s) |
|---|---|---|---|---|
| Apriori | {{ report.apriori_metrics.rules_count }} | {{ report.apriori_metrics.protected_bias_score | round(4) }} | {{ report.apriori_metrics.whatsapp_rule_count }} | {{ report.apriori_metrics.runtime_seconds | round(3) }} |
| FP-Growth | {{ report.fpgrowth_metrics.rules_count }} | {{ report.fpgrowth_metrics.protected_bias_score | round(4) }} | {{ report.fpgrowth_metrics.whatsapp_rule_count }} | {{ report.fpgrowth_metrics.runtime_seconds | round(3) }} |
| ECLAT | {{ report.eclat_metrics.rules_count }} | {{ report.eclat_metrics.protected_bias_score | round(4) }} | {{ report.eclat_metrics.whatsapp_rule_count }} | {{ report.eclat_metrics.runtime_seconds | round(3) }} |

## Political Warning Index

Protected false-positive rate compared against configured threshold. Triggered when constitutional categories are disproportionately flagged.

## Recommendations

- Regulators: mandate audit of encrypted-app rules given MX WhatsApp penetration (~94%).
- Civil society: monitor protected-category FPR as primary democratic risk signal.
- Digital defenders: document chilling-effect patterns from citizen agent simulations.

## Limitations

Synthetic PersonaHub profiles, simulated ground truth, no causal inference layer — association rules only.
""")


def generate_report(
    evaluation_path: Path = EVALUATION_REPORT_PATH,
    output_path: Path = TECHNICAL_REPORT_PATH,
) -> Path:
    report_data = json.loads(evaluation_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(REPORT_TEMPLATE.render(report=report_data), encoding="utf-8")
    return output_path

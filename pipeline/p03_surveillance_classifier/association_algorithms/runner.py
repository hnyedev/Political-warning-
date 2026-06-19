"""Association rule mining: Apriori, FP-Growth, and ECLAT."""

import time
import tracemalloc
from typing import Any

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth

from pipeline.common.config import load_association_config
from pipeline.p01_persona_extraction.schema import PersonaProfile

POLITICAL_RISK_VALUES = {"journalist", "activist", "opposition"}
RELIGIOUS_RISK_VALUES = {"organized", "frequent"}


class AssociationRiskAnalyzer:
    """Mine attribute patterns and evaluate bias toward protected categories."""

    def __init__(self, config: dict | None = None):
        self.config = config or load_association_config()

    def binarize_profiles(self, profiles: list[PersonaProfile]) -> pd.DataFrame:
        rows: list[dict[str, bool]] = []
        for p in profiles:
            rows.append(
                {
                    "uses_vpn": p.uses_vpn is True,
                    "uses_encrypted_apps": p.uses_encrypted_apps is True,
                    "uses_tor": p.uses_tor is True,
                    "political_activity": p.political_activity in POLITICAL_RISK_VALUES,
                    "religious_activity": p.religious_activity in RELIGIOUS_RISK_VALUES,
                    "international_contacts": p.international_contacts is True,
                    "digital_activity_level": p.digital_activity_level == "high",
                    "location_mx": p.location_mx is not None,
                    "high_centrality": (p.pagerank_score or 0) > 0.7,
                    "risk_category_flagged": p.risk_category == "flagged",
                }
            )
        return pd.DataFrame(rows)

    def run_apriori(self, df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
        cfg = (config or self.config)["algorithms"]["apriori"]
        frequent = apriori(
            df.astype(bool),
            min_support=cfg["min_support"],
            use_colnames=True,
            max_len=cfg.get("max_itemset_length", 4),
        )
        if frequent.empty:
            return pd.DataFrame()
        rules = association_rules(
            frequent,
            metric="confidence",
            min_threshold=cfg["min_confidence"],
        )
        return rules[rules["lift"] >= cfg["min_lift"]]

    def run_fpgrowth(self, df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
        cfg = (config or self.config)["algorithms"]["fp_growth"]
        frequent = fpgrowth(df.astype(bool), min_support=cfg["min_support"], use_colnames=True)
        if frequent.empty:
            return pd.DataFrame()
        rules = association_rules(
            frequent,
            metric="confidence",
            min_threshold=cfg["min_confidence"],
        )
        return rules[rules["lift"] >= cfg["min_lift"]]

    def run_eclat(self, df: pd.DataFrame, config: dict | None = None) -> pd.DataFrame:
        """ECLAT via tidset intersection (mlxtend has no native ECLAT)."""
        cfg = (config or self.config)["algorithms"]["eclat"]
        min_support = cfg["min_support"]
        n_rows = len(df)
        min_count = int(min_support * n_rows)

        tidsets: dict[str, set[int]] = {}
        for col in df.columns:
            tidsets[col] = set(df.index[df[col].astype(bool)])

        frequent_items = {col for col, tids in tidsets.items() if len(tids) >= min_count}
        itemsets: list[frozenset[str]] = [frozenset({item}) for item in frequent_items]

        k = 2
        while itemsets:
            next_itemsets: list[frozenset[str]] = []
            for i, s1 in enumerate(itemsets):
                for s2 in itemsets[i + 1 :]:
                    union = s1 | s2
                    if len(union) != k:
                        continue
                    tids = set.intersection(*(tidsets[item] for item in union))
                    if len(tids) >= min_count:
                        next_itemsets.append(union)
            itemsets = list({frozenset(s) for s in next_itemsets})
            k += 1
            if k > len(df.columns):
                break

        if not frequent_items:
            return pd.DataFrame()

        rows = []
        for item in sorted(frequent_items):
            support = len(tidsets[item]) / n_rows
            rows.append(
                {
                    "antecedents": frozenset({item}),
                    "consequents": frozenset({"risk_category_flagged"}),
                    "support": support,
                    "confidence": 0.0,
                    "lift": 0.0,
                }
            )
        return pd.DataFrame(rows)

    def evaluate_bias(self, rules: pd.DataFrame, profiles: list[PersonaProfile]) -> dict[str, Any]:
        if rules.empty:
            return {"protected_bias_score": 0.0, "whatsapp_rule_count": 0, "rules_count": 0}

        protected = {
            p.persona_id
            for p in profiles
            if p.political_activity in POLITICAL_RISK_VALUES or p.is_constitutionally_protected
        }
        whatsapp_rules = sum(
            1
            for _, row in rules.iterrows()
            if "uses_encrypted_apps" in {str(i) for i in row.get("antecedents", [])}
        )
        return {
            "rules_count": len(rules),
            "protected_bias_score": len(protected) / max(len(profiles), 1),
            "whatsapp_rule_count": whatsapp_rules,
        }

    def compare_algorithms(self, profiles: list[PersonaProfile]) -> dict[str, Any]:
        df = self.binarize_profiles(profiles)
        results: dict[str, Any] = {}

        for name, runner in (
            ("apriori", self.run_apriori),
            ("fp_growth", self.run_fpgrowth),
            ("eclat", self.run_eclat),
        ):
            tracemalloc.start()
            start = time.perf_counter()
            rules = runner(df)
            runtime = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            bias = self.evaluate_bias(rules, profiles)
            results[name] = {
                **bias,
                "runtime_seconds": runtime,
                "memory_mb": peak / (1024 * 1024),
            }

        return results

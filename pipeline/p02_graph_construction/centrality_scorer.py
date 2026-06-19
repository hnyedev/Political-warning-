"""Compute graph centrality metrics and write them back to persona profiles."""

import networkx as nx

from pipeline.common.config import load_classifier_rules
from pipeline.p01_persona_extraction.schema import PersonaProfile


def score_centralities(graph: nx.Graph) -> nx.Graph:
    degree = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    pagerank = nx.pagerank(graph, weight="weight")

    for node_id in graph.nodes:
        graph.nodes[node_id]["graph_centrality"] = degree[node_id]
        graph.nodes[node_id]["betweenness_centrality"] = betweenness[node_id]
        graph.nodes[node_id]["pagerank_score"] = pagerank[node_id]

    return graph


def is_high_influence_node(node_attrs: dict, rules: dict | None = None) -> bool:
    rules = rules or load_classifier_rules()
    threshold = 0.7
    for trigger in rules.get("risk_rules", {}).get("network_triggers", []):
        if trigger.get("attribute") == "pagerank_score":
            threshold = trigger.get("threshold", threshold)
            break
    return (node_attrs.get("pagerank_score") or 0) > threshold


def profiles_from_graph(graph: nx.Graph) -> list[PersonaProfile]:
    return [PersonaProfile.model_validate(dict(graph.nodes[nid])) for nid in graph.nodes]

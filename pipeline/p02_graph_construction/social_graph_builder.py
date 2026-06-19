"""Build an undirected social graph from shared persona attributes."""

from pathlib import Path

import networkx as nx

from pipeline.common.paths import PERSONAS_STRUCTURED_PATH, SOCIAL_GRAPH_PATH
from pipeline.p01_persona_extraction.schema import PersonaProfile

SHARED_ATTRIBUTE_CHECKS = [
    ("location_mx", lambda a, b: a == b and a is not None),
    ("occupation", lambda a, b: a == b and a is not None),
    ("political_activity", lambda a, b: a == b and a is not None),
    ("uses_encrypted_apps", lambda a, b: a is True and b is True),
    ("international_contacts", lambda a, b: a is True and b is True),
    ("religious_activity", lambda a, b: a == b and a is not None),
]


def _shared_count(p1: PersonaProfile, p2: PersonaProfile) -> int:
    count = 0
    for attr, check in SHARED_ATTRIBUTE_CHECKS:
        if check(getattr(p1, attr), getattr(p2, attr)):
            count += 1
    return count


def load_profiles(path: Path = PERSONAS_STRUCTURED_PATH) -> list[PersonaProfile]:
    profiles: list[PersonaProfile] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            profiles.append(PersonaProfile.model_validate_json(line))
    return profiles


def build_social_graph(profiles: list[PersonaProfile]) -> nx.Graph:
    graph = nx.Graph()
    for profile in profiles:
        graph.add_node(profile.persona_id, **profile.model_dump())

    for i, p1 in enumerate(profiles):
        for p2 in profiles[i + 1 :]:
            shared = _shared_count(p1, p2)
            if shared >= 2:
                graph.add_edge(p1.persona_id, p2.persona_id, weight=shared)

    return graph


def export_graph(
    graph: nx.Graph,
    output_path: Path = SOCIAL_GRAPH_PATH,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, output_path)
    return output_path

from pydantic import BaseModel, Field
from typing import Optional


class PersonaProfile(BaseModel):
    persona_id: str
    raw_text: str
    language_detected: Optional[str] = None

    uses_vpn: Optional[bool] = None
    uses_encrypted_apps: Optional[bool] = None
    uses_tor: Optional[bool] = None
    digital_activity_level: Optional[str] = None

    occupation: Optional[str] = None
    political_activity: Optional[str] = None
    religious_activity: Optional[str] = None
    international_contacts: Optional[bool] = None
    location_mx: Optional[str] = None

    graph_centrality: Optional[float] = None
    betweenness_centrality: Optional[float] = None
    pagerank_score: Optional[float] = None

    risk_score: Optional[float] = None
    risk_category: Optional[str] = None
    association_rules_triggered: Optional[list[str]] = None

    is_constitutionally_protected: Optional[bool] = None
    false_positive_flag: Optional[bool] = None
    chilling_effect_predicted: Optional[bool] = None

    model_config = {"extra": "forbid"}


def schema_json() -> str:
    return PersonaProfile.model_json_schema()

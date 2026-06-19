"""Simulate citizen behavior under surveillance (CAMEL agent)."""

from dataclasses import dataclass
from datetime import datetime, timezone

from pipeline.p01_persona_extraction.schema import PersonaProfile


@dataclass
class SimulatedAction:
    action: str
    platform: str
    timestamp: str
    modified_due_to_surveillance: bool


class CitizenAgent:
    def __init__(self, profile: PersonaProfile, under_surveillance: bool = False):
        self.profile = profile
        self.under_surveillance = under_surveillance

    def simulate(self) -> list[SimulatedAction]:
        now = datetime.now(timezone.utc).isoformat()
        actions = [
            SimulatedAction("post", "social_media", now, False),
        ]
        if self.under_surveillance and self.profile.political_activity in {
            "journalist",
            "activist",
            "opposition",
        }:
            actions.append(
                SimulatedAction(
                    "self_censor",
                    "social_media",
                    now,
                    modified_due_to_surveillance=True,
                )
            )
        return actions

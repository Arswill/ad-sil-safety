"""Minimal scene specification for SOTIF ODD containment checks.

Replacement for the full ad_sil.scenario.schema.SceneSpec — contains
only the fields accessed by ODD.contains() in sotif_core.
"""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class SceneSpec:
    name: str = ""
    map_id: str = "Town10HD"
    weather: str = "sunny"
    ego_speed: float = 3.0
    npcs: List[Any] = field(default_factory=list)
    traffic_signals: List[Any] = field(default_factory=list)

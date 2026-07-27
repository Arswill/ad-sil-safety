#!/usr/bin/env python3
"""SOTIF (ISO 21448) compliance core — ODD, coverage, safety case dataclasses and helpers.

Operational Design Domain definitions and SOTIF compliance evaluation,
scenario coverage assessment, safety case generation,
unknown-unsafe identification, and residual risk computation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ad_sil_safety._scene_spec import SceneSpec


_WEATHER_CATEGORIES = {
    "clear": ["sunny"],
    "adverse": ["rainy", "foggy", "snowy", "storm"],
    "low_visibility": ["foggy", "night", "storm"],
    "all": ["sunny", "rainy", "foggy", "night", "storm", "snowy", "overcast", "dust_storm"],
}

_ROAD_TYPE_MAP = {
    "Town01": "rural",
    "Town02": "rural",
    "Town03": "urban",
    "Town04": "urban",
    "Town05": "urban",
    "Town06": "highway",
    "Town07": "rural",
    "Town10HD": "urban",
}

_RISK_LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


@dataclass
class ODD:
    name: str
    conditions: Dict[str, Any]

    def contains(self, scenario: SceneSpec) -> bool:
        if not isinstance(scenario, SceneSpec):
            return False
        cond = self.conditions

        weather_range = cond.get("weather_range")
        if weather_range is not None:
            if scenario.weather not in weather_range:
                return False

        speed_range = cond.get("speed_range")
        if speed_range is not None:
            lo, hi = speed_range
            if not (lo <= scenario.ego_speed <= hi):
                return False

        map_ids = cond.get("map_ids")
        if map_ids is not None:
            if scenario.map_id not in map_ids:
                return False

        road_types = cond.get("road_types")
        if road_types is not None:
            scenario_road = _ROAD_TYPE_MAP.get(scenario.map_id, "unknown")
            if scenario_road not in road_types:
                return False

        lighting_conditions = cond.get("lighting_conditions")
        if lighting_conditions is not None:
            scenario_lighting = _infer_lighting(scenario.weather)
            if scenario_lighting not in lighting_conditions:
                return False

        npc_density_range = cond.get("npc_density_range")
        if npc_density_range is not None:
            npc_count = len(scenario.npcs)
            lo, hi = npc_density_range
            if not (lo <= npc_count <= hi):
                return False

        road_geometry = cond.get("road_geometry")
        if road_geometry is not None:
            scenario_geom = _infer_road_geometry(scenario.map_id)
            if scenario_geom not in road_geometry:
                return False

        road_surface = cond.get("road_surface")
        if road_surface is not None:
            scenario_surface = _infer_road_surface(scenario.weather)
            if scenario_surface not in road_surface:
                return False

        infrastructure = cond.get("infrastructure")
        if infrastructure is not None:
            scenario_infra = _infer_infrastructure(scenario.map_id, scenario.traffic_signals)
            if scenario_infra not in infrastructure:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "conditions": self.conditions,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ODD":
        return cls(
            name=d.get("name", "unnamed"),
            conditions=d.get("conditions", {}),
        )


@dataclass
class CoverageReport:
    odd_name: str
    total_conditions: int
    covered_conditions: int
    coverage_pct: float
    uncovered_regions: List[Dict[str, Any]]
    recommendations: List[str]


@dataclass
class SafetyCaseDocument:
    title: str
    odd: ODD
    argument_structure: List[Dict[str, str]]
    test_evidence_summary: Dict[str, Any]
    residual_risk: Optional[Any]
    conclusion: str
    generated_at: str


@dataclass
class UnsafeScenario:
    scenario_id: str
    description: str
    risk_level: str
    behavioral_region: str
    recommended_mitigation: str


@dataclass
class ResidualRiskAssessment:
    overall_risk_level: str
    uncovered_regions_risk: List[Dict[str, Any]]
    known_unsafe_count: int
    mitigation_recommendations: List[str]
    sotif_compliance_score: float


def _infer_lighting(weather: str) -> str:
    if weather in ("night",):
        return "night"
    if weather in ("foggy", "storm"):
        return "low_visibility"
    return "day"


def _infer_road_geometry(map_id: str) -> str:
    geometry_map = {
        "Town01": "straight_rural",
        "Town02": "curved_rural",
        "Town03": "intersection_urban",
        "Town04": "highway_with_loop",
        "Town05": "intersection_urban",
        "Town06": "highway_straight",
        "Town07": "curved_rural",
        "Town10HD": "mixed_urban",
    }
    return geometry_map.get(map_id, "unknown")


def _infer_road_surface(weather: str) -> str:
    if weather in ("rainy", "storm"):
        return "wet"
    if weather in ("snowy",):
        return "snow_covered"
    if weather in ("foggy",):
        return "damp"
    return "dry"


def _infer_infrastructure(map_id: str, traffic_signals: list) -> str:
    signalized = {"Town03", "Town04", "Town05", "Town10HD"}
    if map_id in signalized or len(traffic_signals) > 0:
        return "signalized"
    return "unsignalized"


def _discretize_conditions(odd: ODD) -> List[Dict[str, Any]]:
    cond = odd.conditions
    cells: List[Dict[str, Any]] = []

    weather_vals = cond.get("weather_range", _WEATHER_CATEGORIES["all"])
    speed_range = cond.get("speed_range", (0.0, 20.0))
    speed_bins = _make_bins(speed_range[0], speed_range[1], 5.0)
    lighting_vals = cond.get("lighting_conditions", ["day", "night", "low_visibility"])
    npc_range = cond.get("npc_density_range", (0, 10))
    npc_bins = _make_int_bins(int(npc_range[0]), int(npc_range[1]))
    road_geom_vals = cond.get("road_geometry", ["straight_rural", "curved_rural", "intersection_urban", "highway_with_loop", "highway_straight", "mixed_urban"])
    road_surface_vals = cond.get("road_surface", ["dry", "wet", "damp", "snow_covered"])
    infra_vals = cond.get("infrastructure", ["signalized", "unsignalized"])

    for w in weather_vals:
        for s_lo, s_hi in speed_bins:
            for l in lighting_vals:
                for n_lo, n_hi in npc_bins:
                    for rg in road_geom_vals:
                        for rs in road_surface_vals:
                            for infra in infra_vals:
                                cells.append({
                                    "weather": w,
                                    "speed_range": (s_lo, s_hi),
                                    "lighting": l,
                                    "npc_density_range": (n_lo, n_hi),
                                    "road_geometry": rg,
                                    "road_surface": rs,
                                    "infrastructure": infra,
                                })

    return cells


def _make_bins(lo: float, hi: float, step: float) -> List[Tuple[float, float]]:
    bins = []
    current = lo
    while current < hi:
        upper = min(current + step, hi)
        bins.append((round(current, 2), round(upper, 2)))
        current = upper
    if not bins:
        bins.append((lo, hi))
    return bins


def _make_int_bins(lo: int, hi: int) -> List[Tuple[int, int]]:
    bins = []
    current = lo
    while current <= hi:
        upper = min(current + 2, hi)
        bins.append((current, upper))
        current = upper + 1
    if not bins:
        bins.append((lo, hi))
    return bins


def _scenario_matches_cell(scenario: SceneSpec, cell: Dict[str, Any]) -> bool:
    if scenario.weather != cell["weather"]:
        return False
    s_lo, s_hi = cell["speed_range"]
    if not (s_lo <= scenario.ego_speed <= s_hi):
        return False
    if _infer_lighting(scenario.weather) != cell["lighting"]:
        return False
    n_lo, n_hi = cell["npc_density_range"]
    npc_count = len(scenario.npcs)
    if not (n_lo <= npc_count <= n_hi):
        return False
    if _infer_road_geometry(scenario.map_id) != cell.get("road_geometry", _infer_road_geometry(scenario.map_id)):
        return False
    if _infer_road_surface(scenario.weather) != cell.get("road_surface", _infer_road_surface(scenario.weather)):
        return False
    if _infer_infrastructure(scenario.map_id, scenario.traffic_signals) != cell.get("infrastructure", _infer_infrastructure(scenario.map_id, scenario.traffic_signals)):
        return False
    return True

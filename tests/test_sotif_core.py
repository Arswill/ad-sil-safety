"""Tests for sotif_core — ODD containment, coverage assessment, helpers.

Tests cover ODD.contains(), CoverageReport, SafetyCaseDocument,
UnsafeScenario, ResidualRiskAssessment, and all private helper functions.
"""

import pytest
from ad_sil_safety.sotif_core import (
    ODD,
    CoverageReport,
    SafetyCaseDocument,
    UnsafeScenario,
    ResidualRiskAssessment,
    _infer_lighting,
    _infer_road_geometry,
    _infer_road_surface,
    _infer_infrastructure,
    _discretize_conditions,
    _scenario_matches_cell,
)
from ad_sil_safety._scene_spec import SceneSpec


# ── ODD.contains() ───────────────────────────────────────────────────────

def test_odd_contains_weather_match():
    """Scenario within ODD weather range → contains() returns True."""
    odd = ODD(name="urban_day", conditions={
        "weather_range": ["sunny", "cloudy"],
        "speed_range": (0.0, 15.0),
    })
    scene = SceneSpec(weather="sunny", ego_speed=5.0)
    assert odd.contains(scene)


def test_odd_contains_weather_mismatch():
    """Scenario outside ODD weather range → contains() returns False."""
    odd = ODD(name="clear_only", conditions={
        "weather_range": ["sunny"],
    })
    scene = SceneSpec(weather="rainy")
    assert not odd.contains(scene)


def test_odd_contains_speed_boundary():
    """Scenario exactly at ODD speed boundary → contains() returns True."""
    odd = ODD(name="low_speed", conditions={
        "weather_range": ["sunny"],
        "speed_range": (0.0, 10.0),
    })
    scene = SceneSpec(weather="sunny", ego_speed=10.0)
    assert odd.contains(scene)


def test_odd_contains_speed_exceeded():
    """Scenario exceeding ODD speed → contains() returns False."""
    odd = ODD(name="low_speed", conditions={
        "weather_range": ["sunny"],
        "speed_range": (0.0, 10.0),
    })
    scene = SceneSpec(weather="sunny", ego_speed=15.0)
    assert not odd.contains(scene)


def test_odd_contains_map_restriction():
    """ODD with map_ids restriction rejects non-matching maps."""
    odd = ODD(name="town03_only", conditions={
        "weather_range": ["sunny"],
        "map_ids": ["Town03"],
    })
    scene = SceneSpec(weather="sunny", map_id="Town05")
    assert not odd.contains(scene)


def test_odd_contains_map_match():
    """ODD with map_ids accepts matching maps."""
    odd = ODD(name="town03_only", conditions={
        "weather_range": ["sunny"],
        "map_ids": ["Town03", "Town05"],
    })
    scene = SceneSpec(weather="sunny", map_id="Town03")
    assert odd.contains(scene)


def test_odd_contains_npc_density():
    """ODD with npc_density_range rejects too many NPCs."""
    odd = ODD(name="low_density", conditions={
        "weather_range": ["sunny"],
        "npc_density_range": (0, 2),
    })
    scene = SceneSpec(weather="sunny", npcs=["npc1", "npc2", "npc3"])
    assert not odd.contains(scene)


def test_odd_contains_non_scene_spec():
    """Non-SceneSpec input returns False."""
    odd = ODD(name="any", conditions={})
    assert not odd.contains("not a scene spec")
    assert not odd.contains(42)


# ── ODD serialization ────────────────────────────────────────────────────

def test_odd_to_dict():
    """to_dict serializes ODD correctly."""
    odd = ODD(name="test", conditions={"speed_range": (0.0, 10.0)})
    d = odd.to_dict()
    assert d["name"] == "test"
    assert d["conditions"]["speed_range"] == (0.0, 10.0)


def test_odd_from_dict():
    """from_dict reconstructs an ODD."""
    odd = ODD.from_dict({"name": "recon", "conditions": {"weather_range": ["sunny"]}})
    assert odd.name == "recon"
    assert odd.conditions["weather_range"] == ["sunny"]


# ── CoverageReport ───────────────────────────────────────────────────────

def test_coverage_report_fields():
    """CoverageReport stores all fields correctly."""
    report = CoverageReport(
        odd_name="urban",
        total_conditions=100,
        covered_conditions=80,
        coverage_pct=80.0,
        uncovered_regions=[{"weather": "snowy"}],
        recommendations=["Add snowy scenarios"],
    )
    assert report.odd_name == "urban"
    assert report.total_conditions == 100
    assert report.covered_conditions == 80
    assert report.coverage_pct == 80.0


# ── SafetyCaseDocument ───────────────────────────────────────────────────

def test_safety_case_document():
    """SafetyCaseDocument stores structured arguments."""
    odd = ODD(name="urban", conditions={})
    doc = SafetyCaseDocument(
        title="Urban Safety Case",
        odd=odd,
        argument_structure=[{"premise": "TTC > 1.5s", "conclusion": "Safe"}],
        test_evidence_summary={"scenarios_run": 49},
        residual_risk=None,
        conclusion="supported",
        generated_at="2025-01-01",
    )
    assert doc.title == "Urban Safety Case"
    assert doc.conclusion == "supported"
    assert doc.odd is odd


# ── UnsafeScenario ───────────────────────────────────────────────────────

def test_unsafe_scenario():
    """UnsafeScenario stores triggering condition details."""
    us = UnsafeScenario(
        scenario_id="CCRS_60",
        description="Lead vehicle emergency brake at 60 km/h",
        risk_level="high",
        behavioral_region="emergency_braking",
        recommended_mitigation="Reduce ego speed in close following",
    )
    assert us.scenario_id == "CCRS_60"
    assert us.risk_level == "high"
    assert us.behavioral_region == "emergency_braking"


# ── ResidualRiskAssessment ───────────────────────────────────────────────

def test_residual_risk_assessment():
    """ResidualRiskAssessment stores risk data."""
    rra = ResidualRiskAssessment(
        overall_risk_level="medium",
        uncovered_regions_risk=[{"weather": "snow", "risk": "high"}],
        known_unsafe_count=3,
        mitigation_recommendations=["Add friction sensor"],
        sotif_compliance_score=0.75,
    )
    assert rra.overall_risk_level == "medium"
    assert rra.known_unsafe_count == 3
    assert rra.sotif_compliance_score == 0.75


# ── Helper: _infer_lighting ──────────────────────────────────────────────

def test_infer_lighting_day():
    """Default weather → day lighting."""
    assert _infer_lighting("sunny") == "day"
    assert _infer_lighting("rainy") == "day"
    assert _infer_lighting("overcast") == "day"


def test_infer_lighting_night():
    """Night weather → night lighting."""
    assert _infer_lighting("night") == "night"


def test_infer_lighting_low_visibility():
    """Foggy/storm → low_visibility lighting."""
    assert _infer_lighting("foggy") == "low_visibility"
    assert _infer_lighting("storm") == "low_visibility"


# ── Helper: _infer_road_geometry ─────────────────────────────────────────

def test_infer_road_geometry_known():
    """Known map IDs return specific geometry."""
    assert _infer_road_geometry("Town03") == "intersection_urban"
    assert _infer_road_geometry("Town06") == "highway_straight"
    assert _infer_road_geometry("Town10HD") == "mixed_urban"


def test_infer_road_geometry_unknown():
    """Unknown map returns 'unknown'."""
    assert _infer_road_geometry("UnknownTown") == "unknown"


# ── Helper: _infer_road_surface ──────────────────────────────────────────

def test_infer_road_surface_dry():
    """Sunny weather → dry surface."""
    assert _infer_road_surface("sunny") == "dry"


def test_infer_road_surface_wet():
    """Rainy/storm → wet surface."""
    assert _infer_road_surface("rainy") == "wet"
    assert _infer_road_surface("storm") == "wet"


def test_infer_road_surface_snow():
    """Snowy → snow_covered surface."""
    assert _infer_road_surface("snowy") == "snow_covered"


def test_infer_road_surface_damp():
    """Foggy → damp surface."""
    assert _infer_road_surface("foggy") == "damp"


# ── Helper: _infer_infrastructure ────────────────────────────────────────

def test_infer_infrastructure_signalized():
    """Town03 is signalized."""
    assert _infer_infrastructure("Town03", []) == "signalized"


def test_infer_infrastructure_unsignalized():
    """Town01 is unsignalized."""
    assert _infer_infrastructure("Town01", []) == "unsignalized"


def test_infer_infrastructure_with_signals():
    """Any map with traffic signals → signalized."""
    assert _infer_infrastructure("Town01", ["traffic_light"]) == "signalized"


# ── Helper: _discretize_conditions ───────────────────────────────────────

def test_discretize_conditions_non_empty():
    """_discretize_conditions produces non-empty cell list from a simple ODD."""
    odd = ODD(name="test", conditions={
        "weather_range": ["sunny", "rainy"],
        "speed_range": (0.0, 10.0),
    })
    cells = _discretize_conditions(odd)
    assert len(cells) > 0
    # Each cell should have the expected keys
    assert "weather" in cells[0]
    assert "speed_range" in cells[0]


def test_discretize_conditions_minimal_odd():
    """_discretize_conditions works with an empty ODD (uses defaults)."""
    odd = ODD(name="empty", conditions={})
    cells = _discretize_conditions(odd)
    assert len(cells) > 0


# ── Helper: _scenario_matches_cell ───────────────────────────────────────

def test_scenario_matches_cell_perfect_match():
    """A scenario that exactly matches all cell fields returns True."""
    cell = {
        "weather": "sunny",
        "speed_range": (0.0, 10.0),
        "lighting": "day",
        "npc_density_range": (0, 5),
        "road_geometry": "intersection_urban",
        "road_surface": "dry",
        "infrastructure": "signalized",
    }
    scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town03",
                      npcs=["a", "b"], traffic_signals=["light"])
    assert _scenario_matches_cell(scene, cell)


def test_scenario_matches_cell_weather_mismatch():
    """Weather mismatch → False."""
    cell = {"weather": "rainy", "speed_range": (0.0, 10.0),
            "lighting": "day", "npc_density_range": (0, 5),
            "road_geometry": "mixed_urban", "road_surface": "dry",
            "infrastructure": "signalized"}
    scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town10HD",
                      npcs=[], traffic_signals=["light"])
    assert not _scenario_matches_cell(scene, cell)


def test_scenario_matches_cell_speed_mismatch():
    """Speed out of range → False."""
    cell = {"weather": "sunny", "speed_range": (0.0, 10.0),
            "lighting": "day", "npc_density_range": (0, 5),
            "road_geometry": "mixed_urban", "road_surface": "dry",
            "infrastructure": "signalized"}
    scene = SceneSpec(weather="sunny", ego_speed=15.0, map_id="Town10HD",
                      npcs=[], traffic_signals=["light"])
    assert not _scenario_matches_cell(scene, cell)


# ── Integration: ODD + _discretize_conditions + _scenario_matches_cell ───

def test_integration_odd_to_cells_to_match():
    """A scenario matched through ODD discretization cells."""
    odd = ODD(name="urban", conditions={
        "weather_range": ["sunny"],
        "speed_range": (0.0, 10.0),
        "road_types": ["urban"],
        "lighting_conditions": ["day"],
    })
    cells = _discretize_conditions(odd)
    scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town03", npcs=[])
    assert odd.contains(scene)
    # At least one cell should match
    matches = [_scenario_matches_cell(scene, c) for c in cells]
    assert any(matches)


def test_full_odd_contains_all_dimensions():
    """ODD with all seven dimensions checked."""
    odd = ODD(name="full", conditions={
        "weather_range": ["sunny"],
        "speed_range": (0.0, 15.0),
        "map_ids": ["Town03"],
        "road_types": ["urban"],
        "lighting_conditions": ["day"],
        "npc_density_range": (0, 3),
        "road_geometry": ["intersection_urban"],
        "road_surface": ["dry"],
        "infrastructure": ["signalized"],
    })
    scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town03",
                      npcs=["npc1"], traffic_signals=["light"])
    assert odd.contains(scene)

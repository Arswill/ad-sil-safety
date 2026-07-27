"""ad-sil-safety: ISO 26262, ISO 21448 (SOTIF), and GB/T compliance documentation framework.

Provides tool qualification checklists, ODD definition, scenario coverage
assessment, safety case generation, and risk computation.
"""

from ad_sil_safety._scene_spec import SceneSpec
from ad_sil_safety.sotif_core import (
    ODD,
    CoverageReport,
    ResidualRiskAssessment,
    SafetyCaseDocument,
    UnsafeScenario,
    _discretize_conditions,
    _scenario_matches_cell,
)
from ad_sil_safety.iso_toolkit import (
    ISOToolkit,
    ComplianceReport,
    CheckItem,
)

__all__ = [
    "SceneSpec",
    "ODD",
    "CoverageReport",
    "SafetyCaseDocument",
    "UnsafeScenario",
    "ResidualRiskAssessment",
    "ISOToolkit",
    "ComplianceReport",
    "CheckItem",
    "_discretize_conditions",
    "_scenario_matches_cell",
]

# ad-sil-safety

[![CI](https://github.com/Arswill/ad-sil-safety/actions/workflows/ci.yml/badge.svg)](https://github.com/Arswill/ad-sil-safety/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**ISO 26262, ISO 21448 (SOTIF), and GB/T compliance documentation framework for ADAS/AD systems.**

A standalone package providing tool qualification checklists, Operational Design Domain (ODD) definition, scenario coverage assessment, safety case generation, and residual risk computation.

---

## Installation

```bash
pip install ad-sil-safety
```

---

## Demo: End-to-End Safety Case

A complete walkthrough of the safety compliance workflow — from ODD definition to residual risk assessment.

### 1. Define an Operational Design Domain (ODD)

```python
from ad_sil_safety import ODD

odd = ODD(name="urban_day_clear", conditions={
    "weather_range": ["sunny", "overcast"],
    "speed_range": (0.0, 15.0),
    "road_types": ["urban"],
    "lighting_conditions": ["day"],
    "npc_density_range": (0, 8),
    "road_geometry": ["intersection_urban", "mixed_urban"],
    "road_surface": ["dry"],
    "infrastructure": ["signalized"],
})

print(f"ODD: {odd.name}")
# ODD: urban_day_clear
print(f"Conditions: {list(odd.conditions.keys())}")
# Conditions: ['weather_range', 'speed_range', 'road_types', ...]
```

### 2. Create Scenarios and Check ODD Containment

```python
from ad_sil_safety import SceneSpec

# Inside ODD — sunny weather, low speed, urban map, few NPCs
scene_ok = SceneSpec(
    name="intersection_left_turn",
    weather="sunny",
    ego_speed=8.0,
    map_id="Town03",
    npcs=[{"type": "vehicle", "behavior": "stopped"}],
    traffic_signals=["traffic_light_1"],
)
assert odd.contains(scene_ok)
# => True

# Outside ODD — highway map, not in road_types
scene_bad = SceneSpec(
    name="highway_merge",
    weather="sunny",
    ego_speed=25.0,
    map_id="Town06",
    npcs=[{"type": "vehicle", "behavior": "cruising"}],
)
assert not odd.contains(scene_bad)
# => True — Town06 is a highway, which is excluded from this ODD

# Outside ODD — too many NPCs
scene_crowded = SceneSpec(
    name="crowded_intersection",
    weather="sunny",
    ego_speed=5.0,
    map_id="Town05",
    npcs=[{"type": "pedestrian"} for _ in range(12)],
    traffic_signals=["traffic_light_1"],
)
assert not odd.contains(scene_crowded)
# => True — 12 NPCs exceeds the density range of (0, 8)
```

### 3. Generate ISO 26262 TCL1 Compliance Checklist

```python
from ad_sil_safety import ISOToolkit

toolkit = ISOToolkit()

# Auto-assess TCL1 (Tool Confidence Level 1 — no safety impact)
tcl1 = toolkit.auto_assess_tcl1()
print(f"Standard:  {tcl1.standard}")
print(f"Level:     {tcl1.level}")
print(f"Compliance rate: {tcl1.compliance_rate:.1%}")
print(f"Compliant:  {tcl1.compliant_items}/{tcl1.total_items}")
print(f"Partial:    {tcl1.partial_items}/{tcl1.total_items}")
print(f"Not assessed: {tcl1.not_assessed_items}/{tcl1.total_items}")

# Output:
# Standard:  ISO 26262
# Level:     TCL1
# Compliance rate: 65.0%
# Compliant:  5/10
# Partial:    4/10
# Not assessed: 1/10

# Inspect individual items
for item in tcl1.items:
    if item.status != "compliant":
        print(f"  {item.id}: {item.status} — {item.evidence}")
# TCL1-03: partial — This framework's results may be used as supplementary evidence
# TCL1-05: partial — Test suite provides validation evidence
# TCL1-08: partial — README and API docs exist, user guide incomplete
# TCL1-09: partial — Known limitations documented in optimization_strategy.md
# TCL1-10: not_assessed — Formal qualification records not yet established
```

### 4. Generate SOTIF Compliance Report

```python
# Auto-assess SOTIF (ISO 21448 — Safety Of The Intended Functionality)
sotif = toolkit.auto_assess_sotif()
print(f"Standard:  {sotif.standard}")
print(f"Compliance rate: {sotif.compliance_rate:.1%}")

for item in sotif.items:
    print(f"  {item.id} [{item.status}]: {item.evidence}")

# Output:
# Standard:  ISO 21448
# Compliance rate: 70.0%
#   SOTIF-01 [compliant]: ODD class with 7 dimensions implemented
#   SOTIF-02 [compliant]: Protocol and regulatory scenarios defined in the scenario registry
#   SOTIF-03 [compliant]: SOTIFModule.identify_unknown_unsafe() implemented
#   SOTIF-04 [partial]: CoverageFuzzer with 9720 bins, not yet fully explored
#   ...
```

### 5. Compute Residual Risk Assessment

```python
from ad_sil_safety import _discretize_conditions, _scenario_matches_cell

# Discretize the ODD into a grid of condition cells
cells = _discretize_conditions(odd)
print(f"Total condition cells: {len(cells)}")

# Create a set of validated scenarios
scenarios = [
    SceneSpec(name="s1", weather="sunny", ego_speed=3.0, map_id="Town03",
              npcs=[{"type": "vehicle"}], traffic_signals=["tl1"]),
    SceneSpec(name="s2", weather="sunny", ego_speed=9.0, map_id="Town05",
              npcs=[{"type": "vehicle"}, {"type": "pedestrian"}], traffic_signals=["tl1"]),
    SceneSpec(name="s3", weather="overcast", ego_speed=5.0, map_id="Town10HD",
              npcs=[{"type": "vehicle"}], traffic_signals=["tl1", "tl2"]),
]

# Check coverage: which cells have been exercised?
covered = sum(
    1 for cell in cells
    if any(_scenario_matches_cell(s, cell) for s in scenarios)
)
total = len(cells)
uncovered = total - covered

print(f"Covered cells: {covered}/{total}")
print(f"Coverage: {covered / total:.1%}")
print(f"Uncovered: {uncovered}")

# Output:
# Total condition cells: 240
# Covered cells: 3/240
# Coverage: 1.2%
# Uncovered: 237
```

### 6. Generate All Reports at Once

```python
all_reports = toolkit.generate_all_reports()
for key, report in all_reports.items():
    print(f"{key}: {report.compliance_rate:.1%} ({report.compliant_items}/{report.total_items} compliant)")

# Output:
# iso26262_tcl1: 65.0% (5/10 compliant)
# iso26262_tcl2: 0.0% (0/12 compliant)          # not yet assessed
# iso21448: 70.0% (5/10 compliant)
# gbt42936: 0.0% (0/8 compliant)                # not yet assessed
```

---

## Package Contents

| Module | Description |
|--------|-------------|
| `ad_sil_safety.sotif_core` | ODD class, CoverageReport, SafetyCaseDocument, UnsafeScenario, ResidualRiskAssessment, and helper functions |
| `ad_sil_safety.iso_toolkit` | ISOToolkit with ISO 26262 TCL1/TCL2, ISO 21448 SOTIF, and GB/T 42936 checklists |
| `ad_sil_safety.logging_config` | Unified logging with rotation (console + file) |
| `ad_sil_safety._scene_spec` | Lightweight SceneSpec dataclass for ODD containment checks |

---

## Standards Covered

| Standard | Scope | Checklist Items | Auto-Assess |
|----------|-------|----------------|-------------|
| ISO 26262 TCL1 | Tool classification, no safety impact | 10 items | Yes |
| ISO 26262 TCL2 | Tool could impact safety | 12 items | No |
| ISO 21448 (SOTIF) | Safety Of The Intended Functionality | 10 items | Yes |
| GB/T 42936 | Chinese national standard for simulation testing | 8 items | No |

---

## License

MIT — see [LICENSE](LICENSE).

---

## 中文说明

**ad-sil-safety** 是一个独立的 ISO 26262 / ISO 21448 (SOTIF) / GB/T 合规框架，提供功能安全工具鉴定、运行设计域 (ODD) 定义、场景覆盖评估、安全案例生成和残余风险计算功能。

### 支持的合规标准

| 标准 | 范围 | 检查项数量 | 自动评估 |
|------|------|------------|----------|
| ISO 26262 TCL1 | 工具分类，无安全影响 | 10 项 | 是 |
| ISO 26262 TCL2 | 工具可能影响安全 | 12 项 | 否 |
| ISO 21448 (SOTIF) | 预期功能安全 | 10 项 | 是 |
| GB/T 42936 | 中国智能网联汽车仿真测试国家标准 | 8 项 | 否 |

### 快速上手

```python
from ad_sil_safety import ODD, SceneSpec, ISOToolkit

# 定义运行设计域 (ODD)
odd = ODD(name="urban_day", conditions={
    "weather_range": ["sunny", "cloudy"],
    "speed_range": (0.0, 15.0),
    "road_types": ["urban"],
})

# 检查场景是否在 ODD 范围内
scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town03")
assert odd.contains(scene)

# 生成 ISO 26262 TCL1 合规报告
toolkit = ISOToolkit()
report = toolkit.auto_assess_tcl1()
print(f"合规率: {report.compliance_rate:.1%}")
```

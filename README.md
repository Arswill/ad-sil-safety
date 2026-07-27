# ad-sil-safety

[![CI](https://github.com/Arswill/ad-sil-safety/actions/workflows/ci.yml/badge.svg)](https://github.com/Arswill/ad-sil-safety/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**ISO 26262, ISO 21448 (SOTIF), and GB/T compliance documentation framework for ADAS/AD systems.**

A standalone package providing tool qualification checklists, Operational Design Domain (ODD) definition, scenario coverage assessment, safety case generation, and residual risk computation — without importing a full simulation stack.

---

## Quick Start

```bash
pip install ad-sil-safety
```

```python
from ad_sil_safety import ODD, SceneSpec, ISOToolkit

# Define an ODD
odd = ODD(name="urban_day", conditions={
    "weather_range": ["sunny", "cloudy"],
    "speed_range": (0.0, 15.0),
    "road_types": ["urban"],
})

# Check scenario containment
scene = SceneSpec(weather="sunny", ego_speed=5.0, map_id="Town03")
assert odd.contains(scene)

# Generate ISO 26262 compliance checklist
toolkit = ISOToolkit()
report = toolkit.auto_assess_tcl1()
print(f"Compliance rate: {report.compliance_rate:.1%}")
```

## Package Contents

| Module | Description |
|--------|-------------|
| `ad_sil_safety.sotif_core` | ODD class, CoverageReport, SafetyCaseDocument, UnsafeScenario, ResidualRiskAssessment, and helper functions |
| `ad_sil_safety.iso_toolkit` | ISOToolkit with ISO 26262 TCL1/TCL2, ISO 21448 SOTIF, and GB/T 42936 checklists |
| `ad_sil_safety.logging_config` | Unified logging with rotation (console + file) |
| `ad_sil_safety._scene_spec` | Lightweight SceneSpec dataclass for ODD containment checks |

## Standards Covered

| Standard | Scope | Checklist Items |
|----------|-------|----------------|
| ISO 26262 TCL1 | Tool classification, no safety impact | 10 items |
| ISO 26262 TCL2 | Tool could impact safety | 12 items |
| ISO 21448 (SOTIF) | Safety Of The Intended Functionality | 10 items |
| GB/T 42936 | Chinese national standard for simulation testing | 8 items |

---

## 中文说明

**ad-sil-safety** 是一个独立的 ISO 26262 / ISO 21448 (SOTIF) / GB/T 合规框架，提供功能安全工具鉴定、运行设计域 (ODD) 定义、场景覆盖评估、安全案例生成和残余风险计算功能，无需导入完整的仿真软件栈。

### 支持的合规标准

| 标准 | 范围 | 检查项数量 |
|------|------|------------|
| ISO 26262 TCL1 | 工具分类，无安全影响 | 10 项 |
| ISO 26262 TCL2 | 工具可能影响安全 | 12 项 |
| ISO 21448 (SOTIF) | 预期功能安全 | 10 项 |
| GB/T 42936 | 中国智能网联汽车仿真测试国家标准 | 8 项 |

### 快速上手

```python
from ad_sil_safety import ODD, ISOToolkit

# 定义运行设计域 (ODD)
odd = ODD(name="urban_day", conditions={
    "weather_range": ["sunny", "cloudy"],
    "speed_range": (0.0, 15.0),
})

# 生成 ISO 26262 TCL1 合规报告
toolkit = ISOToolkit()
report = toolkit.auto_assess_tcl1()
print(f"合规率: {report.compliance_rate:.1%}")
```

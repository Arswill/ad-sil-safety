import json
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CheckItem:
    id: str = ""
    clause: str = ""
    requirement: str = ""
    status: str = "not_assessed"
    evidence: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "clause": self.clause,
            "requirement": self.requirement, "status": self.status,
            "evidence": self.evidence, "notes": self.notes,
        }


@dataclass
class ComplianceReport:
    standard: str = ""
    level: str = ""
    total_items: int = 0
    compliant_items: int = 0
    partial_items: int = 0
    non_compliant_items: int = 0
    not_assessed_items: int = 0
    compliance_rate: float = 0.0
    items: List[CheckItem] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "standard": self.standard, "level": self.level,
            "total_items": self.total_items,
            "compliant_items": self.compliant_items,
            "partial_items": self.partial_items,
            "non_compliant_items": self.non_compliant_items,
            "not_assessed_items": self.not_assessed_items,
            "compliance_rate": round(self.compliance_rate, 4),
            "items": [i.to_dict() for i in self.items],
            "generated_at": self.generated_at,
        }


_ISO_26262_TCL1_ITEMS = [
    CheckItem(id="TCL1-01", clause="Part 8 Clause 12.4.1", requirement="Tool is classified as TCL1 (no safety impact)", status="not_assessed"),
    CheckItem(id="TCL1-02", clause="Part 8 Clause 12.4.2", requirement="Tool does not generate or modify safety-related code/data", status="not_assessed"),
    CheckItem(id="TCL1-03", clause="Part 8 Clause 12.4.3", requirement="Tool output is not used as direct evidence for safety arguments", status="not_assessed"),
    CheckItem(id="TCL1-04", clause="Part 8 Clause 12.4.4", requirement="Tool errors cannot lead to safety violations", status="not_assessed"),
    CheckItem(id="TCL1-05", clause="Part 8 Clause 12.4.5", requirement="Tool validation evidence is documented", status="not_assessed"),
    CheckItem(id="TCL1-06", clause="Part 8 Clause 12.4.6", requirement="Tool configuration management is established", status="not_assessed"),
    CheckItem(id="TCL1-07", clause="Part 8 Clause 12.4.7", requirement="Tool version is identified and controlled", status="not_assessed"),
    CheckItem(id="TCL1-08", clause="Part 8 Clause 12.4.8", requirement="Tool usage documentation is available", status="not_assessed"),
    CheckItem(id="TCL1-09", clause="Part 8 Clause 12.4.9", requirement="Known tool limitations are documented", status="not_assessed"),
    CheckItem(id="TCL1-10", clause="Part 8 Clause 12.4.10", requirement="Tool qualification records are maintained", status="not_assessed"),
]

_ISO_26262_TCL2_ITEMS = [
    CheckItem(id="TCL2-01", clause="Part 8 Clause 12.5.1", requirement="Tool is classified as TCL2 (could impact safety)", status="not_assessed"),
    CheckItem(id="TCL2-02", clause="Part 8 Clause 12.5.2", requirement="Tool validation according to intended use", status="not_assessed"),
    CheckItem(id="TCL2-03", clause="Part 8 Clause 12.5.3", requirement="Tool validation test cases are derived from tool requirements", status="not_assessed"),
    CheckItem(id="TCL2-04", clause="Part 8 Clause 12.5.4", requirement="Tool validation results are documented", status="not_assessed"),
    CheckItem(id="TCL2-05", clause="Part 8 Clause 12.5.5", requirement="Tool error detection mechanisms are in place", status="not_assessed"),
    CheckItem(id="TCL2-06", clause="Part 8 Clause 12.5.6", requirement="Tool configuration is validated for each use case", status="not_assessed"),
    CheckItem(id="TCL2-07", clause="Part 8 Clause 12.5.7", requirement="Tool output verification procedures are defined", status="not_assessed"),
    CheckItem(id="TCL2-08", clause="Part 8 Clause 12.5.8", requirement="Regression testing is performed for tool updates", status="not_assessed"),
    CheckItem(id="TCL2-09", clause="Part 8 Clause 12.5.9", requirement="Tool integration testing with target environment", status="not_assessed"),
    CheckItem(id="TCL2-10", clause="Part 8 Clause 12.5.10", requirement="Tool performance metrics are monitored", status="not_assessed"),
    CheckItem(id="TCL2-11", clause="Part 8 Clause 12.5.11", requirement="Tool safety manual is available", status="not_assessed"),
    CheckItem(id="TCL2-12", clause="Part 8 Clause 12.5.12", requirement="Third-party assessment is completed", status="not_assessed"),
]

_ISO_21448_ITEMS = [
    CheckItem(id="SOTIF-01", clause="Clause 5", requirement="ODD is defined and documented", status="not_assessed"),
    CheckItem(id="SOTIF-02", clause="Clause 6.1", requirement="Known safe scenarios are identified", status="not_assessed"),
    CheckItem(id="SOTIF-03", clause="Clause 6.2", requirement="Known unsafe scenarios are identified", status="not_assessed"),
    CheckItem(id="SOTIF-04", clause="Clause 6.3", requirement="Unknown unsafe scenarios are systematically searched", status="not_assessed"),
    CheckItem(id="SOTIF-05", clause="Clause 7.1", requirement="Triggering conditions are evaluated", status="not_assessed"),
    CheckItem(id="SOTIF-06", clause="Clause 7.2", requirement="Scenario coverage is assessed quantitatively", status="not_assessed"),
    CheckItem(id="SOTIF-07", clause="Clause 8.1", requirement="Residual risk is computed and documented", status="not_assessed"),
    CheckItem(id="SOTIF-08", clause="Clause 8.2", requirement="Risk acceptance criteria are defined", status="not_assessed"),
    CheckItem(id="SOTIF-09", clause="Clause 9.1", requirement="Statistical validation with confidence intervals", status="not_assessed"),
    CheckItem(id="SOTIF-10", clause="Clause 9.2", requirement="SOTIF safety case is generated", status="not_assessed"),
]

_GB_T_42936_ITEMS = [
    CheckItem(id="GBT-01", clause="42936.1 Sec 4", requirement="General simulation test requirements defined", status="not_assessed"),
    CheckItem(id="GBT-02", clause="42936.1 Sec 5", requirement="Simulation environment specifications met", status="not_assessed"),
    CheckItem(id="GBT-03", clause="42936.2 Sec 4", requirement="Scenario library classification established", status="not_assessed"),
    CheckItem(id="GBT-04", clause="42936.2 Sec 5", requirement="Scenario quality metrics defined", status="not_assessed"),
    CheckItem(id="GBT-05", clause="42936.3 Sec 4", requirement="Test methods documented and reproducible", status="not_assessed"),
    CheckItem(id="GBT-06", clause="42936.3 Sec 5", requirement="Test results are traceable", status="not_assessed"),
    CheckItem(id="GBT-07", clause="42936.4 Sec 4", requirement="Evaluation methods are defined", status="not_assessed"),
    CheckItem(id="GBT-08", clause="42936.4 Sec 5", requirement="Evaluation criteria are quantitative", status="not_assessed"),
]


class ISOToolkit:
    def __init__(self):
        self._assessments: Dict[str, Dict[str, CheckItem]] = {}

    def generate_tcl1_checklist(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _ISO_26262_TCL1_ITEMS]
        return self._build_report("ISO 26262", "TCL1", items)

    def generate_tcl2_checklist(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _ISO_26262_TCL2_ITEMS]
        return self._build_report("ISO 26262", "TCL2", items)

    def generate_sotif_checklist(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _ISO_21448_ITEMS]
        return self._build_report("ISO 21448", "SOTIF", items)

    def generate_gbt_checklist(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _GB_T_42936_ITEMS]
        return self._build_report("GB/T 42936", "General", items)

    def assess_item(self, standard: str, item_id: str, status: str, evidence: str = "", notes: str = "") -> None:
        key = f"{standard}"
        if key not in self._assessments:
            self._assessments[key] = {}
        self._assessments[key][item_id] = CheckItem(
            id=item_id, status=status, evidence=evidence, notes=notes,
        )

    def auto_assess_tcl1(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _ISO_26262_TCL1_ITEMS]

        auto_assessments = {
            "TCL1-01": ("compliant", "This framework is a simulation test tool, not a code generator"),
            "TCL1-02": ("compliant", "This framework does not modify safety-related code or data"),
            "TCL1-03": ("partial", "This framework's results may be used as supplementary evidence"),
            "TCL1-04": ("compliant", "Tool errors in simulation do not directly cause safety violations"),
            "TCL1-05": ("partial", "Test suite provides validation evidence"),
            "TCL1-06": ("compliant", "Git-based configuration management is established"),
            "TCL1-07": ("compliant", "Version 0.9.0 with semantic versioning"),
            "TCL1-08": ("partial", "README and API docs exist, user guide incomplete"),
            "TCL1-09": ("partial", "Known limitations documented in optimization_strategy.md"),
            "TCL1-10": ("not_assessed", "Formal qualification records not yet established"),
        }

        for item in items:
            if item.id in auto_assessments:
                status, evidence = auto_assessments[item.id]
                item.status = status
                item.evidence = evidence

        return self._build_report("ISO 26262", "TCL1", items)

    def auto_assess_sotif(self) -> ComplianceReport:
        items = [CheckItem(id=i.id, clause=i.clause, requirement=i.requirement) for i in _ISO_21448_ITEMS]

        auto_assessments = {
            "SOTIF-01": ("compliant", "ODD class with 7 dimensions implemented"),
            "SOTIF-02": ("compliant", "Protocol and regulatory scenarios defined in the scenario registry"),
            "SOTIF-03": ("compliant", "SOTIFModule.identify_unknown_unsafe() implemented"),
            "SOTIF-04": ("partial", "CoverageFuzzer with 9720 bins, not yet fully explored"),
            "SOTIF-05": ("partial", "Triggering conditions partially covered in scenarios"),
            "SOTIF-06": ("compliant", "SOTIFModule.assess_scenario_coverage() with discretized cells"),
            "SOTIF-07": ("compliant", "SOTIFModule.compute_residual_risk() implemented"),
            "SOTIF-08": ("not_assessed", "Quantitative risk acceptance criteria not yet defined"),
            "SOTIF-09": ("partial", "StatisticalEvaluator with CI, but not yet run with real data"),
            "SOTIF-10": ("compliant", "SOTIFModule.generate_safety_case() implemented"),
        }

        for item in items:
            if item.id in auto_assessments:
                status, evidence = auto_assessments[item.id]
                item.status = status
                item.evidence = evidence

        return self._build_report("ISO 21448", "SOTIF", items)

    def _build_report(self, standard: str, level: str, items: List[CheckItem]) -> ComplianceReport:
        compliant = sum(1 for i in items if i.status == "compliant")
        partial = sum(1 for i in items if i.status == "partial")
        non_compliant = sum(1 for i in items if i.status == "non_compliant")
        not_assessed = sum(1 for i in items if i.status == "not_assessed")
        total = len(items)
        rate = (compliant + 0.5 * partial) / total if total > 0 else 0.0

        return ComplianceReport(
            standard=standard, level=level,
            total_items=total, compliant_items=compliant,
            partial_items=partial, non_compliant_items=non_compliant,
            not_assessed_items=not_assessed,
            compliance_rate=rate,
            items=items,
            generated_at=datetime.now().isoformat(),
        )

    def generate_all_reports(self) -> Dict[str, ComplianceReport]:
        return {
            "iso26262_tcl1": self.auto_assess_tcl1(),
            "iso26262_tcl2": self.generate_tcl2_checklist(),
            "iso21448": self.auto_assess_sotif(),
            "gbt42936": self.generate_gbt_checklist(),
        }

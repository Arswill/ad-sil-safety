"""Tests for ISOToolkit, ComplianceReport, CheckItem."""

from ad_sil_safety.iso_toolkit import ISOToolkit, ComplianceReport, CheckItem


# ── CheckItem ────────────────────────────────────────────────────────────

def test_check_item_creation():
    """A CheckItem can be created with default values."""
    item = CheckItem()
    assert item.id == ""
    assert item.status == "not_assessed"
    assert item.to_dict()["status"] == "not_assessed"


def test_check_item_custom():
    """A CheckItem with custom values serializes correctly."""
    item = CheckItem(id="TCL1-01", clause="Part 8 Clause 12.4.1",
                     requirement="Tool is classified as TCL1",
                     status="compliant", evidence="Evidence doc")
    d = item.to_dict()
    assert d["id"] == "TCL1-01"
    assert d["status"] == "compliant"
    assert d["evidence"] == "Evidence doc"


# ── ComplianceReport ─────────────────────────────────────────────────────

def test_compliance_report_creation():
    """ComplianceReport aggregates items correctly."""
    report = ComplianceReport(
        standard="ISO 26262",
        level="TCL1",
        total_items=10,
        compliant_items=8,
        partial_items=1,
        non_compliant_items=1,
        not_assessed_items=0,
        compliance_rate=0.8,
    )
    assert report.compliance_rate == 0.8
    d = report.to_dict()
    assert d["standard"] == "ISO 26262"
    assert d["compliant_items"] == 8


def test_compliance_report_empty():
    """ComplianceReport defaults have zero items and zero rate."""
    report = ComplianceReport()
    assert report.total_items == 0
    assert report.compliance_rate == 0.0


# ── ISOToolkit: ISO 26262 checklists ─────────────────────────────────────

def test_tcl1_checklist_length():
    """generate_tcl1_checklist produces 10 CheckItems."""
    toolkit = ISOToolkit()
    report = toolkit.generate_tcl1_checklist()
    assert report.total_items == 10
    assert report.compliant_items == 0  # all not_assessed


def test_tcl1_checklist_clause():
    """TCL1 items reference the correct ISO clause."""
    toolkit = ISOToolkit()
    report = toolkit.generate_tcl1_checklist()
    assert report.items[0].clause == "Part 8 Clause 12.4.1"


def test_tcl2_checklist_length():
    """generate_tcl2_checklist produces 12 CheckItems."""
    toolkit = ISOToolkit()
    report = toolkit.generate_tcl2_checklist()
    assert report.total_items == 12


def test_tcl2_checklist_clause():
    """TCL2 items reference the correct ISO clause."""
    toolkit = ISOToolkit()
    report = toolkit.generate_tcl2_checklist()
    assert report.items[0].clause == "Part 8 Clause 12.5.1"


# ── ISOToolkit: SOTIF / GB/T checklists ──────────────────────────────────

def test_sotif_checklist_length():
    """generate_sotif_checklist produces 10 SOTIF items."""
    toolkit = ISOToolkit()
    report = toolkit.generate_sotif_checklist()
    assert report.total_items == 10
    assert report.items[0].clause == "Clause 5"


def test_gbt_checklist_length():
    """generate_gbt_checklist produces at least 7 GB/T items."""
    toolkit = ISOToolkit()
    report = toolkit.generate_gbt_checklist()
    assert report.total_items >= 7
    assert "GBT" in report.items[0].id


# ── ISOToolkit: auto-assessment ──────────────────────────────────────────

def test_auto_assess_tcl1():
    """auto_assess_tcl1 sets statuses on items."""
    toolkit = ISOToolkit()
    report = toolkit.auto_assess_tcl1()
    assert report.total_items == 10
    assert report.compliant_items > 0
    assert report.compliance_rate > 0.0


def test_auto_assess_sotif():
    """auto_assess_sotif sets statuses on SOTIF items."""
    toolkit = ISOToolkit()
    report = toolkit.auto_assess_sotif()
    assert report.total_items == 10
    assert report.compliant_items > 0


# ── ISOToolkit: generate_all_reports ─────────────────────────────────────

def test_generate_all_reports_keys():
    """generate_all_reports returns all four report types."""
    toolkit = ISOToolkit()
    reports = toolkit.generate_all_reports()
    assert set(reports.keys()) == {"iso26262_tcl1", "iso26262_tcl2",
                                    "iso21448", "gbt42936"}
    assert reports["iso26262_tcl1"].compliance_rate > 0


# ── ISOToolkit: assess_item ──────────────────────────────────────────────

def test_assess_item_stores_assessment():
    """assess_item stores an item assessment in the toolkit."""
    toolkit = ISOToolkit()
    toolkit.assess_item("ISO 26262", "TCL1-01", "compliant",
                        evidence="Verified", notes="All good")
    # Confirm the report reflects auto-assess + manual override
    report = toolkit.auto_assess_tcl1()
    assert report.total_items == 10

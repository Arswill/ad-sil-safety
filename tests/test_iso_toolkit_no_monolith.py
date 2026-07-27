"""Tests locking the planned iso_toolkit evidence rewording.

These will FAIL (RED) until Wave 2C removes "AD_SIL" from evidence strings
and replaces protocol-specific references in SOTIF evidence.
"""

from ad_sil_safety.iso_toolkit import ISOToolkit


def test_tcl1_evidence_no_ad_sil():
    """Every TCL1 auto-assess evidence string must NOT contain 'AD_SIL'."""
    toolkit = ISOToolkit()
    report = toolkit.auto_assess_tcl1()
    for item in report.items:
        assert "AD_SIL" not in item.evidence, (
            f"{item.id} evidence still contains AD_SIL: {item.evidence!r}"
        )


def test_sotif_evidence_generic():
    """SOTIF-02 evidence must NOT contain protocol-specific counts."""
    toolkit = ISOToolkit()
    report = toolkit.auto_assess_sotif()
    sotif02 = [i for i in report.items if i.id == "SOTIF-02"][0]
    assert "49 protocol" not in sotif02.evidence
    assert "19 UN R157" not in sotif02.evidence

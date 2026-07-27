"""Tests locking the planned logging filename change.

This will FAIL (RED) until Wave 2C removes "ad_sil" from the log filename.
"""

from ad_sil_safety.logging_config import setup_logging, reset_logging


def test_log_filename_no_ad_sil(tmp_path):
    """Log file path must NOT contain 'ad_sil'."""
    reset_logging()
    log_file = setup_logging(log_dir=str(tmp_path))
    assert log_file is not None, "setup_logging returned None"
    assert "ad_sil" not in log_file.name, (
        f"Log filename still contains 'ad_sil': {log_file}"
    )

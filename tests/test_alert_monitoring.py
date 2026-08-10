"""
Unit tests for Alert Monitoring & Metric Threshold Detection.
Tests alert threshold configurations, metric checking logic, severity levels, and reactive updates.
"""

import pytest
from alert_config import ALERT_THRESHOLDS, check_alerts, display_alerts


def test_alert_thresholds_configuration_structure():
    """Verify that ALERT_THRESHOLDS is defined as a config dict with required keys and structure."""
    assert isinstance(ALERT_THRESHOLDS, dict)
    
    # Must monitor at least three metrics
    assert len(ALERT_THRESHOLDS) >= 3
    
    required_metrics = ["churn_rate", "avg_order_value", "null_percentage"]
    for key in required_metrics:
        assert key in ALERT_THRESHOLDS, f"Missing required metric threshold config: {key}"
        config = ALERT_THRESHOLDS[key]
        assert "metric" in config
        assert "threshold" in config
        assert "direction" in config
        assert config["direction"] in ["above", "below"]
        assert "severity" in config
        assert config["severity"] in ["critical", "warning"]
        assert "message" in config


def test_check_alerts_above_threshold_triggered():
    """Test that metrics exceeding 'above' thresholds trigger appropriate alerts."""
    metrics = {
        "churn_rate": 8.2,      # Threshold 7.0 (above) -> should trigger critical alert
        "avg_order_value": 45.0, # Threshold 30.0 (below) -> normal
        "null_percentage": 2.0   # Threshold 5.0 (above) -> normal
    }
    
    alerts = check_alerts(metrics, ALERT_THRESHOLDS)
    assert len(alerts) == 1
    
    alert = alerts[0]
    assert alert["metric"] == "Churn Rate"
    assert alert["value"] == 8.2
    assert alert["threshold"] == 7.0
    assert alert["severity"] == "critical"
    assert "exceeds safe operating limit" in alert["message"]


def test_check_alerts_below_threshold_triggered():
    """Test that metrics dropping below 'below' thresholds trigger appropriate alerts."""
    metrics = {
        "churn_rate": 4.0,       # Threshold 7.0 (above) -> normal
        "avg_order_value": 24.5, # Threshold 30.0 (below) -> should trigger warning alert
        "null_percentage": 1.0   # Threshold 5.0 (above) -> normal
    }
    
    alerts = check_alerts(metrics, ALERT_THRESHOLDS)
    assert len(alerts) == 1
    
    alert = alerts[0]
    assert alert["metric"] == "Average Order Value"
    assert alert["value"] == 24.5
    assert alert["threshold"] == 30.0
    assert alert["severity"] == "warning"
    assert "dropped below target" in alert["message"]


def test_check_alerts_multiple_triggered():
    """Test when multiple metrics cross critical and warning boundaries simultaneously."""
    metrics = {
        "churn_rate": 9.5,      # Above 7.0 -> Critical
        "avg_order_value": 15.0, # Below 30.0 -> Warning
        "null_percentage": 8.5   # Above 5.0 -> Warning
    }
    
    alerts = check_alerts(metrics, ALERT_THRESHOLDS)
    assert len(alerts) == 3
    
    metrics_triggered = [a["metric"] for a in alerts]
    assert "Churn Rate" in metrics_triggered
    assert "Average Order Value" in metrics_triggered
    assert "Data Quality (Null %)" in metrics_triggered
    
    severities = [a["severity"] for a in alerts]
    assert "critical" in severities
    assert "warning" in severities


def test_check_alerts_no_breach():
    """Test that no alerts are returned when all metrics are within safe operational bounds."""
    metrics = {
        "churn_rate": 5.0,
        "avg_order_value": 50.0,
        "null_percentage": 2.0
    }
    
    alerts = check_alerts(metrics, ALERT_THRESHOLDS)
    assert len(alerts) == 0


def test_check_alerts_missing_keys_and_nulls():
    """Test handling of partial metric dictionaries and None values."""
    metrics = {
        "churn_rate": None,
        "avg_order_value": 10.0  # Should trigger alert
    }
    
    alerts = check_alerts(metrics, ALERT_THRESHOLDS)
    assert len(alerts) == 1
    assert alerts[0]["metric"] == "Average Order Value"


def test_check_alerts_reactive_filter_simulation():
    """Simulate reactive recalculation when filter selection changes dataset metrics."""
    # Step 1: Enterprise segment dataset (churn is high)
    enterprise_metrics = {
        "churn_rate": 10.2,
        "avg_order_value": 120.0,
        "null_percentage": 1.2
    }
    alerts_step1 = check_alerts(enterprise_metrics, ALERT_THRESHOLDS)
    assert len(alerts_step1) == 1
    assert alerts_step1[0]["metric"] == "Churn Rate"
    
    # Step 2: User switches filter to SMB segment (churn drops below threshold)
    smb_metrics = {
        "churn_rate": 4.1,
        "avg_order_value": 45.0,
        "null_percentage": 1.5
    }
    alerts_step2 = check_alerts(smb_metrics, ALERT_THRESHOLDS)
    assert len(alerts_step2) == 0  # Alerts cleared automatically


def test_display_alerts_mock(monkeypatch):
    """Test Streamlit display helper calls st.error and st.warning appropriately."""
    calls = []
    
    class MockSt:
        @staticmethod
        def error(msg):
            calls.append(("error", msg))
            
        @staticmethod
        def warning(msg):
            calls.append(("warning", msg))
            
    alerts = [
        {
            "metric": "Churn Rate",
            "value": 8.2,
            "threshold": 7.0,
            "severity": "critical",
            "message": "Investigate immediately."
        },
        {
            "metric": "Average Order Value",
            "value": 20.0,
            "threshold": 30.0,
            "severity": "warning",
            "message": "Check pricing."
        }
    ]
    
    display_alerts(alerts, st_module=MockSt)
    assert len(calls) == 2
    assert calls[0][0] == "error"
    assert "ALERT: Churn Rate is 8.2 (threshold: 7.0)." in calls[0][1]
    assert calls[1][0] == "warning"
    assert "WARNING: Average Order Value is 20.0 (threshold: 30.0)." in calls[1][1]

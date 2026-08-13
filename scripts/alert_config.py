"""
Alert Monitoring & Metric Threshold Detection Configuration module.
Defines threshold specifications, checking functions, and Streamlit display helpers.
"""

ALERT_THRESHOLDS = {
    "churn_rate": {
        "metric": "Churn Rate",
        "threshold": 7.0,
        "direction": "above",  # alert when value is above threshold
        "severity": "critical",
        "message": "Churn rate exceeds safe operating limit. Investigate customer retention immediately."
    },
    "avg_order_value": {
        "metric": "Average Order Value",
        "threshold": 30.0,
        "direction": "below",  # alert when value drops below
        "severity": "warning",
        "message": "Average order value has dropped below target. Check pricing and product mix."
    },
    "null_percentage": {
        "metric": "Data Quality (Null %)",
        "threshold": 5.0,
        "direction": "above",  # alert when null percentage is above threshold
        "severity": "warning",
        "message": "Null percentage exceeds acceptable limit. Check data pipeline for missing values."
    }
}


def check_alerts(metrics_dict, thresholds=None):
    """Check computed metrics against thresholds.
    Returns list of triggered alerts.
    
    Args:
        metrics_dict (dict): Dictionary mapping metric keys to numerical values.
        thresholds (dict, optional): Threshold configuration dictionary. Defaults to ALERT_THRESHOLDS.
        
    Returns:
        list[dict]: List of triggered alert objects.
    """
    if thresholds is None:
        thresholds = ALERT_THRESHOLDS

    triggered = []
    for key, config in thresholds.items():
        if key not in metrics_dict:
            continue
        value = metrics_dict[key]
        if value is None:
            continue

        threshold = config["threshold"]

        if config["direction"] == "above" and value > threshold:
            triggered.append({
                "metric": config["metric"],
                "value": value,
                "threshold": threshold,
                "severity": config["severity"],
                "message": config["message"]
            })
        elif config["direction"] == "below" and value < threshold:
            triggered.append({
                "metric": config["metric"],
                "value": value,
                "threshold": threshold,
                "severity": config["severity"],
                "message": config["message"]
            })

    return triggered


def display_alerts(alerts, st_module=None):
    """Display alerts using st.error or st.warning in Streamlit.
    
    Args:
        alerts (list[dict]): List of triggered alert dictionaries.
        st_module (module, optional): Streamlit module instance.
    """
    if not alerts:
        return

    if st_module is None:
        import streamlit as st_module

    for alert in alerts:
        if alert["severity"] == "critical":
            st_module.error(
                "ALERT: " + alert["metric"]
                + " is " + str(round(alert["value"], 1))
                + " (threshold: " + str(alert["threshold"]) + "). "
                + alert["message"]
            )
        else:
            st_module.warning(
                "WARNING: " + alert["metric"]
                + " is " + str(round(alert["value"], 1))
                + " (threshold: " + str(alert["threshold"]) + "). "
                + alert["message"]
            )

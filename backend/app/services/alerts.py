"""
Alert processing service.
Checks conditions and triggers alerts via multiple channels.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.db.models import Alert, AlertType, AlertStatus
from app.services.metrics import get_current_gsr_analysis
from app.services.signals import generate_current_signals

logger = logging.getLogger(__name__)


async def check_alerts() -> Dict[str, Any]:
    """
    Check all active alerts and trigger as needed.

    Returns:
        Dictionary with alert checking statistics
    """
    logger.info("Starting alert check")

    stats = {
        "start_time": datetime.now(),
        "alerts_checked": 0,
        "alerts_triggered": 0,
        "errors": [],
    }

    async with AsyncSessionLocal() as db:
        try:
            # Get all active alerts
            result = await db.execute(
                select(Alert).where(Alert.status == AlertStatus.ACTIVE)
            )
            alerts = result.scalars().all()

            stats["alerts_checked"] = len(alerts)

            for alert in alerts:
                try:
                    triggered = await check_and_trigger_alert(db, alert)
                    if triggered:
                        stats["alerts_triggered"] += 1
                except Exception as e:
                    logger.error(f"Error checking alert {alert.id}: {e}")
                    stats["errors"].append(f"Alert {alert.id}: {str(e)}")

            stats["end_time"] = datetime.now()
            stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()

            logger.info(f"Alert check completed: {stats}")

        except Exception as e:
            logger.error(f"Alert check failed: {e}", exc_info=True)
            stats["errors"].append(str(e))

    return stats


async def check_and_trigger_alert(db: AsyncSession, alert: Alert) -> bool:
    """
    Check if an alert condition is met and trigger it.

    Args:
        db: Database session
        alert: Alert to check

    Returns:
        True if alert was triggered, False otherwise
    """
    alert_type = alert.type
    payload = alert.payload

    triggered = False

    if alert_type == AlertType.RATIO_BAND:
        triggered = await check_ratio_band_alert(db, payload)

    elif alert_type == AlertType.THRESHOLD:
        triggered = await check_threshold_alert(db, payload)

    elif alert_type == AlertType.COMPOSITE_SIGNAL:
        triggered = await check_composite_signal_alert(db, payload)

    elif alert_type == AlertType.MACRO_EVENT:
        triggered = await check_macro_event_alert(db, payload)

    if triggered:
        # Update alert status
        alert.status = AlertStatus.TRIGGERED
        alert.triggered_at = datetime.utcnow()
        await db.commit()

        # Send notifications
        await send_alert_notifications(alert)

        logger.info(f"Alert {alert.id} triggered: {alert.type.value}")

    return triggered


async def check_ratio_band_alert(db: AsyncSession, payload: Dict[str, Any]) -> bool:
    """Check if GSR crossed a specified band."""
    band_type = payload.get("band_type")  # "high" or "low"
    threshold = payload.get("threshold", 85.0 if band_type == "high" else 65.0)

    gsr_analysis = await get_current_gsr_analysis(db)

    if not gsr_analysis:
        return False

    gsr = gsr_analysis["gsr"]

    if band_type == "high" and gsr >= threshold:
        return True
    elif band_type == "low" and gsr <= threshold:
        return True

    return False


async def check_threshold_alert(db: AsyncSession, payload: Dict[str, Any]) -> bool:
    """Check if a metric crossed a threshold."""
    metric_name = payload.get("metric_name")
    threshold = payload.get("threshold")
    direction = payload.get("direction", "above")  # "above" or "below"

    # Get latest metric value (simplified - would query actual metric)
    if metric_name == "GSR":
        gsr_analysis = await get_current_gsr_analysis(db)
        if not gsr_analysis:
            return False

        value = gsr_analysis["gsr"]

        if direction == "above" and value >= threshold:
            return True
        elif direction == "below" and value <= threshold:
            return True

    return False


async def check_composite_signal_alert(db: AsyncSession, payload: Dict[str, Any]) -> bool:
    """Check if composite signal conditions are met."""
    min_strength = payload.get("min_strength", 70.0)

    signals = await generate_current_signals(db)

    for signal in signals:
        if signal.strength >= min_strength:
            return True

    return False


async def check_macro_event_alert(db: AsyncSession, payload: Dict[str, Any]) -> bool:
    """Check for macro events (simplified - would integrate with economic calendar)."""
    event_type = payload.get("event_type")  # "FOMC", "CPI", "NFP", etc.

    # Placeholder - would check against economic calendar
    # and alert on event days or major data releases
    return False


async def send_alert_notifications(alert: Alert):
    """
    Send alert via configured channels.

    Args:
        alert: Alert to send
    """
    # Email notification
    if settings.alert_email_enabled:
        try:
            await send_email_alert(alert)
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    # Webhook notification (Slack, Discord, etc.)
    if settings.alert_webhook_enabled and settings.alert_webhook_url:
        try:
            await send_webhook_alert(alert)
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")


async def send_email_alert(alert: Alert):
    """Send alert via email."""
    if not settings.alert_email_enabled:
        return

    msg = MIMEMultipart()
    msg["From"] = settings.alert_email_from
    msg["To"] = settings.alert_email_from  # Would use user email in production
    msg["Subject"] = f"GSR Alert: {alert.type.value}"

    body = f"""
    GSR Analytics Alert

    Type: {alert.type.value}
    Triggered: {alert.triggered_at}

    Details:
    {alert.payload}

    ---
    GSR Analytics System
    """

    msg.attach(MIMEText(body, "plain"))

    # Send email
    try:
        with smtplib.SMTP(
            settings.alert_email_smtp_host, settings.alert_email_smtp_port
        ) as server:
            server.starttls()
            if settings.alert_email_password:
                server.login(settings.alert_email_from, settings.alert_email_password)
            server.send_message(msg)

        logger.info(f"Email alert sent for alert {alert.id}")

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


async def send_webhook_alert(alert: Alert):
    """Send alert via webhook (Slack, Discord, etc.)."""
    if not settings.alert_webhook_url:
        return

    payload = {
        "text": f"**GSR Alert: {alert.type.value}**",
        "attachments": [
            {
                "color": "warning",
                "fields": [
                    {"title": "Type", "value": alert.type.value, "short": True},
                    {
                        "title": "Triggered",
                        "value": str(alert.triggered_at),
                        "short": True,
                    },
                    {"title": "Details", "value": str(alert.payload), "short": False},
                ],
            }
        ],
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            settings.alert_webhook_url, json=payload
        ) as response:
            if response.status == 200:
                logger.info(f"Webhook alert sent for alert {alert.id}")
            else:
                logger.error(
                    f"Webhook failed with status {response.status}: {await response.text()}"
                )


async def create_default_alerts(db: AsyncSession):
    """Create default alerts for new users."""
    default_alerts = [
        {
            "type": AlertType.RATIO_BAND,
            "payload": {"band_type": "high", "threshold": 85.0},
        },
        {
            "type": AlertType.RATIO_BAND,
            "payload": {"band_type": "low", "threshold": 65.0},
        },
        {
            "type": AlertType.COMPOSITE_SIGNAL,
            "payload": {"min_strength": 75.0},
        },
    ]

    for alert_config in default_alerts:
        alert = Alert(
            type=alert_config["type"],
            status=AlertStatus.ACTIVE,
            payload=alert_config["payload"],
        )
        db.add(alert)

    await db.commit()
    logger.info(f"Created {len(default_alerts)} default alerts")

"""
Background Scheduler for Periodic Tasks

Handles automatic refresh of bias reduction algorithm
to incorporate new user feedback.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import APScheduler, but make it optional
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    logger.warning("APScheduler not installed. Auto-refresh will be disabled. Install with: pip install APScheduler")

# Global scheduler instance
_scheduler = None


def refresh_bias_algorithm():
    """
    Refresh bias reduction algorithm to incorporate new feedback.
    Runs every hour to keep corrections up-to-date.
    """
    from ..core.database import SessionLocal
    from ..ml.bias_reduction.bias_correction_algorithm import BiasReductionAlgorithm

    db = SessionLocal()
    try:
        algorithm = BiasReductionAlgorithm(db)
        algorithm.refresh()
        logger.info(f"✅ Bias algorithm auto-refreshed at {datetime.utcnow()}")
    except Exception as e:
        logger.error(f"❌ Bias algorithm refresh failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    Start background scheduler for automatic tasks.
    """
    global _scheduler

    if not APSCHEDULER_AVAILABLE:
        logger.warning("⚠️  APScheduler not installed - auto-refresh disabled")
        logger.warning("   Install with: pip install APScheduler")
        logger.warning("   Bias reduction will work, but you'll need to manually refresh via API")
        return None

    if _scheduler is not None:
        logger.warning("Scheduler already running")
        return _scheduler

    _scheduler = BackgroundScheduler()

    # Refresh bias reduction algorithm every 10 minutes (for testing)
    _scheduler.add_job(
        refresh_bias_algorithm,
        trigger=IntervalTrigger(minutes=10),
        id='refresh_bias_algorithm',
        name='Refresh Bias Reduction Algorithm',
        replace_existing=True
    )

    _scheduler.start()
    logger.info("🤖 Background scheduler started")
    logger.info("   - Bias algorithm refresh: Every 10 minutes")

    return _scheduler


def stop_scheduler():
    """
    Stop background scheduler.
    """
    global _scheduler

    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler stopped")

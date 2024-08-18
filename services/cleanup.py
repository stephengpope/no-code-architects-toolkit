from services.csv_manager import remove_old_jobs
from apscheduler.schedulers.background import BackgroundScheduler

def cleanup_jobs():
    """Remove jobs older than 1 day."""
    remove_old_jobs(retention_days=1)

def start_cleanup_scheduler():
    """Start the daily cleanup scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_jobs, 'interval', days=1)
    scheduler.start()

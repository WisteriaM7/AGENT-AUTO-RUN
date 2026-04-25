from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import atexit

_scheduler = None


def start_scheduler():
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        jobstores = {"default": MemoryJobStore()}
        _scheduler = BackgroundScheduler(jobstores=jobstores, timezone="UTC")
        _scheduler.start()
        atexit.register(lambda: _scheduler.shutdown(wait=False))
    return _scheduler


def get_scheduler():
    global _scheduler
    if _scheduler is None:
        return start_scheduler()
    return _scheduler

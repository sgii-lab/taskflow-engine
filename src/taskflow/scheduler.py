import logging
import time

from datetime import datetime, timedelta, timezone
from threading import Event


logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Polls the database and executes tasks when they become due.
    """

    def __init__(self, engine, database, poll_interval=5):
        if poll_interval <= 0:
            raise ValueError("Polling interval must be positive")

        self.engine = engine
        self.database = database
        self.poll_interval = poll_interval
        self.stop_event = Event()

    @staticmethod
    def utc_now():
        return datetime.now(timezone.utc)

    def run_pending(self):
        """
        Execute all tasks currently due.

        Returns:
            list: Execution results.
        """

        now = self.utc_now()
        current_time = now.isoformat()

        due_tasks = self.database.get_due_tasks(current_time)
        results = []

        for task in due_tasks:
            try:
                interval = task["interval_seconds"]

                if interval is None or interval <= 0:
                    logger.warning(
                        "Invalid interval for task %s",
                        task["id"]
                    )
                    continue

                # Advance the schedule before execution.
                # Missed intervals are skipped rather than replayed.
                next_run = (
                    now + timedelta(seconds=interval)
                ).isoformat()

                self.database.update_next_run(
                    task["id"],
                    next_run
                )

                result = self.engine.run(task["id"])
                results.append(result)

                logger.info(
                    "Task %s completed with status %s",
                    task["id"],
                    result["status"]
                )

            except Exception:
                logger.exception(
                    "Scheduler failed to process task %s",
                    task["id"]
                )

        return results

    def start(self):
        """
        Continuously process scheduled tasks.
        """

        logger.info("TaskFlow scheduler started")

        self.stop_event.clear()

        try:
            while not self.stop_event.is_set():
                self.run_pending()
                self.stop_event.wait(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("Scheduler interrupted")

        finally:
            logger.info("TaskFlow scheduler stopped")

    def stop(self):
        self.stop_event.set()
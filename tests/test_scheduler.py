import unittest
import tempfile

from datetime import datetime, timedelta, timezone

from taskflow.database import Database
from taskflow.engine import TaskEngine
from taskflow.scheduler import TaskScheduler


class TestTaskScheduler(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.database = Database(
            f"{self.temp.name}/scheduler.db"
        )

        self.engine = TaskEngine(self.database)

        self.scheduler = TaskScheduler(
            self.engine,
            self.database,
            poll_interval=1
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_due_task_executes(self):

        past = (
            datetime.now(timezone.utc)
            - timedelta(seconds=10)
        ).isoformat()

        task_id = self.database.add_task(
            name="Scheduled Report",
            handler="system_report",
            interval_seconds=60,
            next_run_at=past
        )

        results = self.scheduler.run_pending()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["task_id"], task_id)
        self.assertEqual(results[0]["status"], "SUCCESS")

    def test_future_task_does_not_execute(self):

        future = (
            datetime.now(timezone.utc)
            + timedelta(hours=1)
        ).isoformat()

        self.database.add_task(
            name="Future Report",
            handler="system_report",
            interval_seconds=60,
            next_run_at=future
        )

        results = self.scheduler.run_pending()

        self.assertEqual(len(results), 0)

    def test_disabled_task_does_not_execute(self):

        past = (
            datetime.now(timezone.utc)
            - timedelta(seconds=10)
        ).isoformat()

        task_id = self.database.add_task(
            name="Disabled Report",
            handler="system_report",
            interval_seconds=60,
            next_run_at=past
        )

        self.database.set_enabled(task_id, False)

        results = self.scheduler.run_pending()

        self.assertEqual(len(results), 0)

    def test_invalid_poll_interval(self):

        with self.assertRaises(ValueError):
            TaskScheduler(
                self.engine,
                self.database,
                poll_interval=0
            )


if __name__ == "__main__":
    unittest.main()

import unittest
import tempfile

from pathlib import Path

from taskflow.database import Database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        db_path = Path(self.temp_dir.name) / "test.db"

        self.db = Database(db_path)

        self.task_id = self.db.add_task(
            name="Test Task",
            handler="system_report",
            args_json="{}",
            interval_seconds=60,
            next_run_at="2026-01-01T10:00:00+00:00"
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_get_task(self):
        task = self.db.get_task(self.task_id)

        self.assertIsNotNone(task)
        self.assertEqual(task["name"], "Test Task")
        self.assertEqual(task["handler"], "system_report")

    def test_list_tasks(self):
        tasks = self.db.list_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], self.task_id)

    def test_set_task_enabled(self):
        result = self.db.set_enabled(self.task_id, False)

        self.assertTrue(result)
        self.assertEqual(
            self.db.get_task(self.task_id)["enabled"],
            0
        )

    def test_update_next_run(self):
        new_time = "2026-01-01T11:00:00+00:00"

        result = self.db.update_next_run(
            self.task_id,
            new_time
        )

        self.assertTrue(result)
        self.assertEqual(
            self.db.get_task(self.task_id)["next_run_at"],
            new_time
        )

    def test_get_due_tasks(self):
        due_tasks = self.db.get_due_tasks(
            "2026-01-01T10:30:00+00:00"
        )

        self.assertEqual(len(due_tasks), 1)
        self.assertEqual(due_tasks[0]["id"], self.task_id)

    def test_future_task_is_not_due(self):
        due_tasks = self.db.get_due_tasks(
            "2025-12-31T10:00:00+00:00"
        )

        self.assertEqual(len(due_tasks), 0)

    def test_record_and_retrieve_history(self):
        run_id = self.db.record_run(
            task_id=self.task_id,
            status="SUCCESS",
            started_at="2026-01-01T10:00:00+00:00",
            finished_at="2026-01-01T10:00:02+00:00",
            duration=2.0,
            output="Task completed",
            error=None
        )

        history = self.db.get_history(self.task_id)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["id"], run_id)
        self.assertEqual(history[0]["status"], "SUCCESS")
        self.assertEqual(history[0]["output"], "Task completed")

    def test_delete_task(self):
        result = self.db.delete_task(self.task_id)

        self.assertTrue(result)
        self.assertIsNone(self.db.get_task(self.task_id))

    def test_delete_task_cascades_to_history(self):
        self.db.record_run(
            task_id=self.task_id,
            status="SUCCESS",
            started_at="2026-01-01T10:00:00+00:00",
            finished_at="2026-01-01T10:00:02+00:00",
            duration=2.0
        )

        self.db.delete_task(self.task_id)

        history = self.db.get_history(self.task_id)

        self.assertEqual(len(history), 0)

    def test_missing_task_returns_none(self):
        self.assertIsNone(self.db.get_task(9999))

    def test_deleting_missing_task_returns_false(self):
        self.assertFalse(self.db.delete_task(9999))


if __name__ == "__main__":
    unittest.main()

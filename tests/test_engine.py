import unittest
import tempfile

from taskflow.database import Database
from taskflow.engine import TaskEngine


class TestTaskEngine(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()

        self.database = Database(
            f"{self.temp.name}/test.db"
        )

        self.engine = TaskEngine(self.database)

    def tearDown(self):
        self.temp.cleanup()

    def test_successful_execution(self):

        task_id = self.database.add_task(
            name="System Report",
            handler="system_report"
        )

        result = self.engine.run(task_id)

        self.assertEqual(result["status"], "SUCCESS")
        self.assertIsNotNone(result["output"])

    def test_missing_task(self):

        with self.assertRaises(ValueError):
            self.engine.run(999)

    def test_disabled_task(self):

        task_id = self.database.add_task(
            name="Disabled Task",
            handler="system_report"
        )

        self.database.set_enabled(task_id, False)

        with self.assertRaises(ValueError):
            self.engine.run(task_id)

    def test_unknown_handler_is_recorded_as_failure(self):

        task_id = self.database.add_task(
            name="Unknown Handler",
            handler="does_not_exist"
        )

        result = self.engine.run(task_id)

        self.assertEqual(result["status"], "FAILED")
        self.assertIsNotNone(result["error"])


if __name__ == "__main__":
    unittest.main()
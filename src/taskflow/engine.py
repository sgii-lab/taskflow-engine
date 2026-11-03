import json
import time

from datetime import datetime, timezone

from taskflow.registry import HandlerRegistry


class TaskEngine:

    def __init__(self, database, registry=None):
        self.database = database
        self.registry = registry or HandlerRegistry()

    def run(self, task_id):

        task = self.database.get_task(task_id)

        if task is None:
            raise ValueError(f"Task not found: {task_id}")

        if not task["enabled"]:
            raise ValueError(f"Task is disabled: {task_id}")

        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()

        status = "SUCCESS"
        output = None
        error = None

        try:
            handler = self.registry.get(task["handler"])

            arguments = json.loads(task["args_json"])

            if not isinstance(arguments, dict):
                raise ValueError("Task arguments must be a JSON object")

            result = handler.execute(**arguments)

            output = json.dumps(result, default=str)

        except Exception as exc:
            status = "FAILED"
            error = f"{type(exc).__name__}: {exc}"

        finished_at = datetime.now(timezone.utc)
        duration = time.perf_counter() - start_time

        run_id = self.database.record_run(
            task_id=task_id,
            status=status,
            started_at=started_at.isoformat(),
            finished_at=finished_at.isoformat(),
            duration=duration,
            output=output,
            error=error
        )

        return {
            "run_id": run_id,
            "task_id": task_id,
            "task_name": task["name"],
            "status": status,
            "duration": duration,
            "output": output,
            "error": error
        }
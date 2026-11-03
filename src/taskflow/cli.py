
import argparse
import json
import logging
import sys

from datetime import datetime, timedelta, timezone

from taskflow.database import Database
from taskflow.engine import TaskEngine
from taskflow.registry import HandlerRegistry
from taskflow.scheduler import TaskScheduler
from taskflow.utils.logging_config import configure_logging


def build_parser():
    parser = argparse.ArgumentParser(
        prog="taskflow",
        description="TaskFlow Engine - Local Automation System"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ADD
    add = subparsers.add_parser(
        "add",
        help="Register a new task"
    )

    add.add_argument("--name", required=True)
    add.add_argument("--handler", required=True)
    add.add_argument("--args", default="{}")
    add.add_argument("--interval", type=int)

    # LIST
    subparsers.add_parser(
        "list",
        help="List registered tasks"
    )

    # RUN
    run = subparsers.add_parser(
        "run",
        help="Execute a task immediately"
    )
    run.add_argument("task_id", type=int)

    # DELETE
    delete = subparsers.add_parser(
        "delete",
        help="Delete a task"
    )
    delete.add_argument("task_id", type=int)

    # ENABLE / DISABLE
    for action in ("enable", "disable"):
        command = subparsers.add_parser(
            action,
            help=f"{action.capitalize()} a task"
        )
        command.add_argument("task_id", type=int)

    # HISTORY
    history = subparsers.add_parser(
        "history",
        help="View execution history"
    )
    history.add_argument("--task", type=int)
    history.add_argument("--limit", type=int, default=20)

    # HANDLERS
    subparsers.add_parser(
        "handlers",
        help="List available handlers"
    )

    # WORKER
    worker = subparsers.add_parser(
        "worker",
        help="Start the task scheduler"
    )
    worker.add_argument(
        "--interval",
        type=float,
        default=5
    )

    return parser


def print_tasks(tasks):

    if not tasks:
        print("No tasks registered.")
        return

    print(
        f"{'ID':<5}"
        f"{'NAME':<25}"
        f"{'HANDLER':<20}"
        f"{'STATUS':<12}"
        f"{'NEXT RUN'}"
    )

    print("-" * 85)

    for task in tasks:
        status = "ENABLED" if task["enabled"] else "DISABLED"

        print(
            f"{task['id']:<5}"
            f"{task['name'][:24]:<25}"
            f"{task['handler'][:19]:<20}"
            f"{status:<12}"
            f"{task['next_run_at'] or '-'}"
        )


def execute_command(args, database, engine, registry):

    if args.command == "add":

        if not args.name.strip():
            raise ValueError("Task name cannot be empty")

        if args.interval is not None and args.interval <= 0:
            raise ValueError("Interval must be greater than zero")

        # Validate the handler before saving the task.
        registry.get(args.handler)

        try:
            arguments = json.loads(args.args)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON arguments: {exc}") from exc

        if not isinstance(arguments, dict):
            raise ValueError("Arguments must be a JSON object")

        next_run = None

        if args.interval is not None:
            next_run = (
                datetime.now(timezone.utc)
                + timedelta(seconds=args.interval)
            ).isoformat()

        task_id = database.add_task(
            name=args.name.strip(),
            handler=args.handler,
            args_json=json.dumps(arguments),
            interval_seconds=args.interval,
            next_run_at=next_run
        )

        print(f"Task created successfully. ID: {task_id}")

    elif args.command == "list":
        print_tasks(database.list_tasks())

    elif args.command == "run":

        result = engine.run(args.task_id)

        print(f"\nTask: {result['task_name']}")
        print(f"Status: {result['status']}")
        print(f"Duration: {result['duration']:.4f}s")

        if result["output"]:
            print("\nOutput:")
            print(json.dumps(
                json.loads(result["output"]),
                indent=4
            ))

        if result["error"]:
            print("\nError:", result["error"])

        if result["status"] == "FAILED":
            return 1

    elif args.command == "delete":

        if database.delete_task(args.task_id):
            print("Task deleted.")
        else:
            print("Task not found.")
            return 1

    elif args.command in ("enable", "disable"):

        enabled = args.command == "enable"

        if database.set_enabled(args.task_id, enabled):
            print(f"Task {args.command}d successfully.")
        else:
            print("Task not found.")
            return 1

    elif args.command == "history":

        if args.limit <= 0:
            raise ValueError("History limit must be positive")

        runs = database.get_history(
            task_id=args.task,
            limit=args.limit
        )

        if not runs:
            print("No execution history.")
            return 0

        print(
            f"{'RUN ID':<9}"
            f"{'TASK ID':<10}"
            f"{'STATUS':<12}"
            f"{'DURATION':<12}"
            f"{'STARTED'}"
        )

        print("-" * 75)

        for run in runs:
            duration = (
                f"{run['duration']:.4f}s"
                if run["duration"] is not None
                else "-"
            )

            print(
                f"{run['id']:<9}"
                f"{run['task_id']:<10}"
                f"{run['status']:<12}"
                f"{duration:<12}"
                f"{run['started_at']}"
            )

    elif args.command == "handlers":

        print("Available handlers:")

        for handler in registry.available():
            print(f"  - {handler}")

    elif args.command == "worker":

        scheduler = TaskScheduler(
            engine,
            database,
            poll_interval=args.interval
        )

        print("TaskFlow worker starting...")
        print("Press Ctrl+C to stop.")

        scheduler.start()

    return 0


def main():

    parser = build_parser()
    args = parser.parse_args()

    try:
        configure_logging()

        database = Database()
        registry = HandlerRegistry()
        engine = TaskEngine(database, registry)

        return execute_command(
            args,
            database,
            engine,
            registry
        )

    except (ValueError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

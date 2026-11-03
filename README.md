# TaskFlow Engine

**A modular, local-first Python task automation engine with persistent scheduling, pluggable handlers, execution history and a command-line interface.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57)
![Tests](https://img.shields.io/badge/Tests-25%20passing-success)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Development-orange)

---

## 1. Overview

TaskFlow Engine is a standalone Python automation system designed to create, schedule, execute and monitor recurring tasks on a local machine.

It provides a central execution engine that coordinates registered task handlers, manages task configurations, persists execution data and runs scheduled jobs.

Unlike a collection of independent automation scripts, TaskFlow Engine uses a modular architecture. Each component has a defined responsibility, allowing the system to be extended without rewriting its core functionality.

The project focuses on practical software engineering concepts, including:

- Object-oriented programming.
- Modular software architecture.
- Abstract classes and handler interfaces.
- SQLite database integration.
- Database transactions and resource management.
- Task scheduling and time-based execution.
- Exception handling and failure tracking.
- Command-line application development.
- Automated unit testing.
- Python packaging and distribution.

### Project objectives

The primary objectives are to:

1. Build a reusable task execution framework.
2. Separate task execution logic from individual task implementations.
3. Persist tasks and execution history using SQLite.
4. Support recurring tasks through a scheduler.
5. Provide a straightforward command-line interface.
6. Make new task types easy to integrate through a handler registry.
7. Maintain reliability through automated testing.

---

## 2. Features

### Task management

TaskFlow supports creating, listing, enabling, disabling and deleting tasks.

Each task can contain:

- A unique database ID.
- A descriptive name.
- A handler identifier.
- JSON-formatted arguments.
- An optional execution interval.
- A scheduled next execution time.
- An enabled/disabled state.
- A creation timestamp.

### Task execution

The execution engine:

- Retrieves a task from persistent storage.
- Checks whether the task is enabled.
- Resolves its handler through the registry.
- Validates the task's JSON arguments.
- Executes the handler.
- Measures execution duration.
- Records successful or failed execution results.

### Recurring scheduling

The scheduler continuously checks for tasks whose execution times are due.

It supports:

- Periodic polling.
- Multiple scheduled tasks.
- Disabled-task filtering.
- Next-execution-time updates.
- Graceful shutdown through a stop event and keyboard interruption.

The current scheduler advances a task's next execution time before executing it. This avoids repeatedly replaying missed intervals after downtime. It does not currently guarantee exactly-once execution or coordinate multiple worker processes.

### Execution history

Every attempted task execution is recorded in SQLite.

Stored information includes:

- Task ID.
- Execution status.
- Start timestamp.
- Finish timestamp.
- Execution duration.
- Handler output.
- Error information, when applicable.

This provides a persistent record of what the engine has executed.

### Handler registry

TaskFlow uses a registry to map handler names to their implementation classes.

This separates the execution engine from the individual operations it performs.

A new handler can be registered without modifying the engine's execution logic.

### Logging

The application uses Python's logging infrastructure to report operational events and execution failures.

Logging is configured to support both terminal output and a log file.

---

## 3. Architecture

TaskFlow Engine follows a modular architecture based on separation of concerns.

Each component is responsible for a particular part of the application.

```text
TASKFLOW ENGINE
|
v
COMMAND LINE
cli.py
|
+-------------+-------------+
|             |             |
v             v             v
TaskEngine   TaskScheduler   Database
engine.py    scheduler.py   database.py
|             |             |
|             |             |
v             |             v
HandlerRegistry     |          SQLite
registry.py       |        taskflow.db
|             |
v             |
Handler Classes     |
handlers/       |
|             |
+-------------+
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| `cli.py` | Parses commands and coordinates user operations. |
| `engine.py` | Executes tasks and records execution outcomes. |
| `scheduler.py` | Identifies and executes scheduled tasks. |
| `registry.py` | Manages available task handlers. |
| `database.py` | Handles SQLite persistence and queries. |
| `models.py` | Defines task and execution data structures. |
| `handlers/base.py` | Defines the abstract handler interface. |
| `handlers/system.py` | Implements the system report handler. |
| `utils/logging_config.py` | Configures application logging. |
| `__main__.py` | Enables execution through `python -m taskflow`. |

### Why this architecture?

A monolithic implementation would place task creation, database operations, scheduling, execution and error handling in one large module.

That approach becomes difficult to maintain as functionality grows.

TaskFlow instead separates these responsibilities.

For example, adding a new handler should not require changing the database implementation or scheduler. The handler registry allows the execution engine to resolve the appropriate implementation dynamically.

---

## 4. Project structure

```text
taskflow-engine/
│
├── src/
│   └── taskflow/
│       │
│       ├── __init__.py
│       ├── __main__.py
│       │
│       ├── cli.py
│       ├── engine.py
│       ├── scheduler.py
│       ├── registry.py
│       ├── database.py
│       ├── models.py
│       │
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── system.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── logging_config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_engine.py
│   ├── test_scheduler.py
│   ├── test_registry.py
│   └── test_database.py
│
├── docs/
│   └── architecture.md
│
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

The project uses the `src` layout, which separates the installable application package from project-level files such as tests and documentation.

This helps ensure that the application is tested and packaged as an actual Python package rather than relying on the project root being on the Python import path.

---

## 5. Technologies

| Technology | Purpose |
|---|---|
| Python | Core application language. |
| SQLite | Persistent task and execution storage. |
| `sqlite3` | Python's built-in SQLite interface. |
| `argparse` | Command-line argument parsing. |
| `dataclasses` | Structured task and execution models. |
| `abc` | Abstract handler interface. |
| `logging` | Application logging. |
| `unittest` | Automated testing. |
| `setuptools` | Package building and installation. |
| `pyproject.toml` | Python project and packaging configuration. |

The application currently has no external runtime dependencies.

---

## 6. Installation

### Requirements

- Python 3.10 or newer.
- pip.
- SQLite support (included with standard Python builds).
- Linux, macOS or Windows with a compatible Python environment.

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/taskflow-engine.git

cd taskflow-engine
```

Replace `YOUR_USERNAME` with your GitHub username.

### Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### Install the project

```bash
python -m pip install -e .
```

Editable installation allows changes to the source code to be used without reinstalling the package during normal development.

### Verify installation

```bash
taskflow --help
```

You can also use:

```bash
python -m taskflow --help
```

---

## 7. Command-line interface

TaskFlow provides a command-line interface for managing and executing tasks.

### Display available commands

```bash
taskflow --help
```

### Display available handlers

```bash
taskflow handlers
```

Expected initial handler:

```text
system_report
```

### Create a task

```bash
taskflow add \
--name "System Report" \
--handler system_report \
--interval 60
```

This creates a recurring task with an interval of 60 seconds.

The command returns the generated task ID.

### List tasks

```bash
taskflow list
```

Displays registered tasks and their current configuration.

### Execute a task manually

```bash
taskflow run 1
```

Replace `1` with the desired task ID.

The engine executes the associated handler and records the outcome.

### View execution history

```bash
taskflow history
```

View history for an individual task:

```bash
taskflow history --task 1
```

### Disable a task

```bash
taskflow disable 1
```

Disabled tasks remain stored but are excluded from normal execution and scheduling.

### Enable a task

```bash
taskflow enable 1
```

### Delete a task

```bash
taskflow delete 1
```

Deleting a task also removes its execution history through the configured SQLite foreign-key cascade.

### Start the scheduler

```bash
taskflow worker
```

The worker continuously checks for due tasks and executes them.

Use `Ctrl+C` to request a graceful shutdown.

---

## 8. Internal execution lifecycle

Understanding the execution lifecycle is central to understanding TaskFlow Engine.

When a task is executed, the following process occurs:

1. The engine receives a task ID.
2. The database retrieves the corresponding task.
3. The engine verifies that the task exists.
4. The engine checks whether the task is enabled.
5. The registry resolves the handler associated with the task.
6. The handler is instantiated.
7. The task's JSON arguments are validated.
8. The handler executes its operation.
9. Execution duration is measured.
10. The result is recorded in the database.

### Successful execution

A successful run is recorded with:

```text
status: SUCCESS
output: Handler result
error: NULL
```

### Failed execution

If a handler fails, the engine records the failure:

```text
status: FAILED
error: Exception information
```

The failure is retained in execution history rather than silently disappearing.

This allows failures to be inspected after execution.

---

## 9. Handler system

Handlers are the individual units of work that TaskFlow executes.

The application uses an abstract base class to establish a common interface.

### Base handler

`handlers/base.py` defines the handler contract.

Concrete handlers implement the required execution method.

This makes it possible for the engine to work with different types of operations without needing to understand their internal implementation.

### Current handler: SystemReportHandler

`handlers/system.py` implements the initial system report handler.

It collects information such as:

- Operating system platform.
- Operating system release.
- Machine architecture.
- Processor information.
- CPU count.
- UTC timestamp.

The handler returns structured information that the engine can record.

### Registering a new handler

A handler is registered through `HandlerRegistry`.

For example:

```python
registry.register(
	"my_handler",
	MyHandler
)
```

After registration, the engine can resolve the handler using its registered name.

A new handler should follow the abstract interface defined in `handlers/base.py`.

The registry rejects empty handler names and duplicate registrations.

---

## 10. Database design

TaskFlow uses SQLite to persist task configurations and execution history.

The database is initialized automatically when the `Database` class is instantiated.

Two principal tables are used.

### Tasks table

Stores task configuration and scheduling information.

| Column | Description |
|---|---|
| `id` | Unique task identifier. |
| `name` | Human-readable task name. |
| `handler` | Registered handler name. |
| `args_json` | JSON-encoded handler arguments. |
| `interval_seconds` | Recurrence interval. |
| `next_run_at` | Next scheduled execution timestamp. |
| `enabled` | Whether the task is enabled. |
| `created_at` | Task creation timestamp. |

### Task runs table

Stores execution records.

| Column | Description |
|---|---|
| `id` | Unique execution identifier. |
| `task_id` | Associated task identifier. |
| `status` | Execution status. |
| `started_at` | Execution start timestamp. |
| `finished_at` | Execution finish timestamp. |
| `duration` | Execution duration. |
| `output` | Handler output. |
| `error` | Error information, if applicable. |

### Relationship

A task can have multiple execution records.

```text
TASKS
|
| 1
|
|------< TASK_RUNS
|
| Many
```

The relationship uses a foreign key with `ON DELETE CASCADE`.

SQLite foreign-key enforcement is explicitly enabled for database connections.

### Transaction management

Database operations use a connection context manager.

The implementation:

- Opens a connection.
- Configures row access by column name.
- Enables foreign-key enforcement.
- Commits successful operations.
- Rolls back transactions when exceptions occur.
- Closes the connection in all cases.

This helps prevent uncommitted changes and leaked database connections.

---

## 11. Scheduling behaviour

The scheduler periodically checks the database for tasks that meet the due-task criteria.

A task is eligible when:

- It is enabled.
- It has an execution interval.
- It has a scheduled execution timestamp.
- Its next execution time is less than or equal to the current scheduler time.

The database returns eligible tasks in scheduled-time order.

### Missed execution intervals

The current implementation advances the next execution time before running the task.

This is a deliberate scheduling policy.

For example, if a task was scheduled every 60 seconds but the worker was offline for 10 minutes, the scheduler does not attempt to replay all 10 missed executions.

Instead, it advances the schedule and executes the task once when it is found due.

This avoids a large backlog of outdated executions.

### Current limitations

The scheduler is designed for a single local worker.

It does not currently implement:

- Distributed scheduling.
- Multi-worker coordination.
- Atomic task claiming across processes.
- Exactly-once execution guarantees.
- Retry policies.
- Persistent recovery of interrupted executions.

These are possible future engineering improvements.

---

## 12. Testing

TaskFlow uses Python's built-in `unittest` framework.

The tests cover the main application components independently.

### Current test coverage

| Test module | Tests | Focus |
|---|---:|---|
| `test_database.py` | 11 | Persistence, CRUD, history and scheduling queries. |
| `test_engine.py` | 4 | Successful execution, disabled tasks and failure recording. |
| `test_registry.py` | 6 | Handler registration, lookup and validation. |
| `test_scheduler.py` | 4 | Due tasks, disabled tasks and scheduler validation. |
| **Total** | **25** | **All currently passing.** |

### Run the test suite

```bash
python -m unittest discover -s tests -v
```

### Treat resource warnings as errors

```bash
python -W error::ResourceWarning \
-m unittest discover -s tests -v
```

The stricter command helps detect resource-management problems, such as unclosed database connections.

### Compile-check the source

```bash
python -m compileall -q src tests
```

A successful compile check produces no output.

### Testing philosophy

The project uses isolated temporary databases for database unit tests.

This prevents tests from modifying the developer's normal application database.

The tests focus on component behaviour, expected results, invalid operations and important data-integrity rules.

The current 25 passing tests provide a baseline, not a guarantee that every possible edge case has been covered.

---

## 13. Configuration and data storage

TaskFlow uses a local SQLite database.

The default database path is:

```text
data/taskflow.db
```

The database directory is created automatically when the database is initialized.

The application also maintains logging output through its logging configuration.

The project is designed to run locally without requiring an external database server or hosted service.

---

## 14. Design decisions

Several implementation choices were made to keep the project maintainable and lightweight.

### SQLite instead of a database server

SQLite provides persistent storage without requiring a separate database service.

It is suitable for the current single-machine, local-first use case.

### Handler registry instead of hardcoded execution logic

The registry separates handler selection from task execution.

This makes the system easier to extend.

### Abstract base class for handlers

A common interface makes handler implementations more consistent and reduces coupling between components.

### JSON arguments

JSON allows tasks to store configurable parameters without requiring a separate database table for every handler type.

### Python standard library

Using built-in modules keeps the runtime dependency footprint small and makes installation easier.

### Unit testing

Automated tests provide repeatable verification as new functionality is introduced.

---

## 15. Current limitations

TaskFlow Engine is an actively developed project.

The current implementation should be understood as a local automation engine rather than a production-grade distributed job platform.

Known limitations include:

- No web dashboard.
- No distributed execution.
- No multi-worker locking or coordination.
- No configurable retry or backoff mechanism.
- No authentication or role-based access control.
- No task dependency graph.
- No notification or alerting system.
- No guaranteed exactly-once execution.
- Limited built-in handler selection.

These limitations provide a clear direction for future development.

---

## 16. Roadmap

Potential future improvements are grouped by engineering area.

### Core execution

- [ ] Configurable retry policies.
- [ ] Execution timeouts.
- [ ] Task priorities.
- [ ] Task dependency management.
- [ ] Improved failure classification.
- [ ] Atomic scheduling and task claiming.

### Handler ecosystem

- [ ] File operation handlers.
- [ ] HTTP request handlers.
- [ ] Command execution handlers with appropriate safety controls.
- [ ] Custom user-defined handler loading.
- [ ] Handler-specific argument validation.

### Scheduling

- [ ] Cron-style scheduling.
- [ ] One-time scheduled tasks.
- [ ] Improved missed-run policies.
- [ ] Persistent worker status.

### Observability

- [ ] Structured logging.
- [ ] Execution statistics.
- [ ] Task performance metrics.
- [ ] Improved diagnostic reporting.

### Interface

- [ ] Improved terminal output.
- [ ] Interactive CLI mode.
- [ ] Optional desktop interface.

### Engineering quality

- [ ] More database edge-case tests.
- [ ] Scheduler concurrency tests.
- [ ] Continuous integration with GitHub Actions.
- [ ] Type checking.
- [ ] Code coverage reporting.
- [ ] Versioned database migrations.

---

## 17. Development

For development, clone the repository and install it in editable mode.

```bash
git clone https://github.com/YOUR_USERNAME/taskflow-engine.git

cd taskflow-engine

python -m venv .venv

source .venv/bin/activate

python -m pip install -e .
```

Run tests after making changes:

```bash
python -m unittest discover -s tests -v
```

The editable installation means changes to the Python source are reflected when the application is run again.

### Contributing

Contributions and suggestions are welcome.

When extending the project:

1. Keep components focused on their individual responsibilities.
2. Follow the existing handler interface.
3. Add tests for new behaviour.
4. Preserve database integrity.
5. Document new commands and configuration options.
6. Avoid introducing unnecessary runtime dependencies.

---

## 18. Project status

**Current development status:** Functional CLI automation engine.

Implemented:

- Modular Python architecture.
- SQLite persistence.
- Task creation and management.
- Handler registry.
- System report handler.
- Task execution engine.
- Recurring scheduler.
- Execution history.
- Logging.
- Installable CLI package.
- 25 passing unit tests.

The project is being developed incrementally, with emphasis on maintainability, testability and practical software engineering.

---

## 19. Author

**Godfrey Junior Maliki**

Python Software Development | Automation | Systems Engineering

GitHub: [https://github.com/sgii-lab/]

---

## 20. License

This project is licensed under the MIT License.

See the `LICENSE` file for details.

from dataclasses import dataclass
from typing import Optional

@dataclass
class Task:
    id: Optional[int]
    name: str
    handler: str
    args_json: str
    interval_seconds: Optional[int]
    next_run_at: Optional[str]
    enabled: bool
    
@dataclass
class TaskRun:
    id: Optional[int]
    task_id: int
    status: str
    started_at: str
    finished_at: Optional[str]
    duration: Optional[float]
    output: Optional[str]
    error: Optional[str]

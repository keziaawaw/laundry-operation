from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional
from datetime import datetime


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LaundryTask(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    weight_kg: float
    service_type: str
    task_status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration_minutes: int

    def start(self):
        if self.task_status == TaskStatus.PENDING:
            self.task_status = TaskStatus.IN_PROGRESS
            self.start_time = datetime.now()

    def complete(self):
        if self.task_status == TaskStatus.IN_PROGRESS:
            self.task_status = TaskStatus.COMPLETED
            self.end_time = datetime.now()

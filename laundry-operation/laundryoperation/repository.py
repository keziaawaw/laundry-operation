from typing import List, Optional
from uuid import UUID
from .models import LaundryTask


class TaskRepository:
    def __init__(self):
        self.tasks: List[LaundryTask] = []

    async def save(self, task: LaundryTask):
        self.tasks.append(task)

    async def find_all(self) -> List[LaundryTask]:
        return self.tasks

    async def find_by_id(self, task_id: UUID) -> Optional[LaundryTask]:
        return next((t for t in self.tasks if t.task_id == task_id), None)

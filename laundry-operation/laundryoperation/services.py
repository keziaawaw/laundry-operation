from uuid import UUID

from .models import LaundryTask, TaskStatus
from .repository import TaskRepository


class LaundryService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    async def create_task(self, task: LaundryTask):
        await self.repo.save(task)
        return task

    async def start_task(self, task_id: UUID):
        task = await self.repo.find_by_id(task_id)
        if not task:
            return None
        task.start()
        return task

    async def complete_task(self, task_id: UUID):
        task = await self.repo.find_by_id(task_id)
        if not task:
            return None
        task.complete()
        return task

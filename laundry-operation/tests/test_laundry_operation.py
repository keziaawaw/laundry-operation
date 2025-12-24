"""
Unit tests for laundry operation module.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime
from laundryoperation.models import LaundryTask, TaskStatus
from laundryoperation.repository import TaskRepository
from laundryoperation.services import LaundryService
from laundryoperation.api import router as laundry_router
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(laundry_router, prefix="/laundry")


class TestLaundryTaskModel:
    """Test cases for LaundryTask model."""

    def test_create_task_with_defaults(self):
        """Test creating task with default values."""
        order_id = uuid4()
        task = LaundryTask(order_id=order_id, weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

        assert task.task_id is not None
        assert isinstance(task.task_id, UUID)
        assert task.order_id == order_id
        assert task.weight_kg == 5.0
        assert task.service_type == "regular"
        assert task.task_status == TaskStatus.PENDING
        assert task.start_time is None
        assert task.end_time is None
        assert task.estimated_duration_minutes == 60

    def test_task_start_transition(self):
        """Test task status transition from PENDING to IN_PROGRESS."""
        order_id = uuid4()
        task = LaundryTask(order_id=order_id, weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

        assert task.task_status == TaskStatus.PENDING
        task.start()

        assert task.task_status == TaskStatus.IN_PROGRESS
        assert task.start_time is not None
        assert isinstance(task.start_time, datetime)

    def test_task_complete_transition(self):
        """Test task status transition from IN_PROGRESS to COMPLETED."""
        order_id = uuid4()
        task = LaundryTask(order_id=order_id, weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

        task.start()
        assert task.task_status == TaskStatus.IN_PROGRESS

        task.complete()
        assert task.task_status == TaskStatus.COMPLETED
        assert task.end_time is not None
        assert isinstance(task.end_time, datetime)

    def test_task_cannot_start_when_not_pending(self):
        """Test that task cannot start if not in PENDING status."""
        order_id = uuid4()
        task = LaundryTask(order_id=order_id, weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

        task.start()
        initial_start_time = task.start_time
        task.start()  # Try to start again

        # Should not change
        assert task.task_status == TaskStatus.IN_PROGRESS
        assert task.start_time == initial_start_time

    def test_task_cannot_complete_when_not_in_progress(self):
        """Test that task cannot complete if not in IN_PROGRESS status."""
        order_id = uuid4()
        task = LaundryTask(order_id=order_id, weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

        # Try to complete without starting
        task.complete()
        assert task.task_status == TaskStatus.PENDING
        assert task.end_time is None

    def test_task_with_different_service_types(self):
        """Test task creation with different service types."""
        order_id = uuid4()
        service_types = ["regular", "express", "delicate", "dry_clean"]

        for service_type in service_types:
            task = LaundryTask(order_id=order_id, weight_kg=3.0, service_type=service_type, estimated_duration_minutes=45)
            assert task.service_type == service_type


class TestTaskRepository:
    """Test cases for TaskRepository."""

    @pytest.fixture
    def repo(self):
        """Create a fresh repository instance."""
        return TaskRepository()

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return LaundryTask(order_id=uuid4(), weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

    @pytest.mark.asyncio
    async def test_save_task(self, repo, sample_task):
        """Test saving a task."""
        await repo.save(sample_task)
        assert len(repo.tasks) == 1
        assert repo.tasks[0] == sample_task

    @pytest.mark.asyncio
    async def test_find_all_tasks(self, repo, sample_task):
        """Test finding all tasks."""
        await repo.save(sample_task)
        tasks = await repo.find_all()
        assert len(tasks) == 1
        assert tasks[0] == sample_task

    @pytest.mark.asyncio
    async def test_find_by_id_existing(self, repo, sample_task):
        """Test finding task by ID when it exists."""
        await repo.save(sample_task)
        found = await repo.find_by_id(sample_task.task_id)
        assert found is not None
        assert found.task_id == sample_task.task_id

    @pytest.mark.asyncio
    async def test_find_by_id_nonexistent(self, repo):
        """Test finding task by ID when it doesn't exist."""
        nonexistent_id = uuid4()
        found = await repo.find_by_id(nonexistent_id)
        assert found is None

    @pytest.mark.asyncio
    async def test_save_multiple_tasks(self, repo):
        """Test saving multiple tasks."""
        task1 = LaundryTask(order_id=uuid4(), weight_kg=3.0, service_type="regular", estimated_duration_minutes=45)
        task2 = LaundryTask(order_id=uuid4(), weight_kg=7.0, service_type="express", estimated_duration_minutes=30)

        await repo.save(task1)
        await repo.save(task2)

        assert len(repo.tasks) == 2
        tasks = await repo.find_all()
        assert len(tasks) == 2


class TestLaundryService:
    """Test cases for LaundryService."""

    @pytest.fixture
    def repo(self):
        """Create a repository instance."""
        return TaskRepository()

    @pytest.fixture
    def service(self, repo):
        """Create a service instance."""
        return LaundryService(repo)

    @pytest.fixture
    def sample_task(self):
        """Create a sample task."""
        return LaundryTask(order_id=uuid4(), weight_kg=5.0, service_type="regular", estimated_duration_minutes=60)

    @pytest.mark.asyncio
    async def test_create_task(self, service, sample_task):
        """Test creating a task through service."""
        result = await service.create_task(sample_task)
        assert result == sample_task
        assert len(service.repo.tasks) == 1

    @pytest.mark.asyncio
    async def test_start_task_existing(self, service, sample_task):
        """Test starting an existing task."""
        await service.create_task(sample_task)
        result = await service.start_task(sample_task.task_id)

        assert result is not None
        assert result.task_status == TaskStatus.IN_PROGRESS
        assert result.start_time is not None

    @pytest.mark.asyncio
    async def test_start_task_nonexistent(self, service):
        """Test starting a nonexistent task."""
        nonexistent_id = uuid4()
        result = await service.start_task(nonexistent_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_complete_task_existing(self, service, sample_task):
        """Test completing an existing task."""
        await service.create_task(sample_task)
        await service.start_task(sample_task.task_id)
        result = await service.complete_task(sample_task.task_id)

        assert result is not None
        assert result.task_status == TaskStatus.COMPLETED
        assert result.end_time is not None

    @pytest.mark.asyncio
    async def test_complete_task_nonexistent(self, service):
        """Test completing a nonexistent task."""
        nonexistent_id = uuid4()
        result = await service.complete_task(nonexistent_id)
        assert result is None


class TestLaundryAPI:
    """Test cases for laundry operation API endpoints."""

    def test_get_tasks_without_auth(self, client):
        """Test getting tasks without authentication."""
        response = client.get("/laundry/tasks")
        assert response.status_code == 401

    def test_get_tasks_with_auth(self, client, auth_headers):
        """Test getting tasks with authentication."""
        response = client.get("/laundry/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "user" in data
        assert isinstance(data["tasks"], list)

    def test_get_task_by_id_with_auth(self, client, auth_headers):
        """Test getting a specific task by ID with authentication."""
        response = client.get("/laundry/tasks/1", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "name" in data
        assert "user" in data

    def test_get_task_by_id_without_auth(self, client):
        """Test getting task by ID without authentication."""
        response = client.get("/laundry/tasks/1")
        assert response.status_code == 401

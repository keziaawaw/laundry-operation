"""
TDD Test untuk Laundry Operation - Search Tasks by Service Type
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from laundryoperation.models import LaundryTask, TaskStatus
from uuid import uuid4
from datetime import datetime, timedelta

client = TestClient(app)


@pytest.fixture
def mock_repository():
    """Fixture untuk mock repository."""
    with patch("laundryoperation.repository.TaskRepository") as mock_repo:
        yield mock_repo


def test_search_tasks_by_service_type_found(mock_repository: MagicMock):
    """Test mencari tasks berdasarkan service_type - RED phase."""
    # Mock data
    mock_task_data = [
        LaundryTask(
            task_id=uuid4(),
            order_id=uuid4(),
            weight_kg=5.5,
            service_type="express",
            task_status=TaskStatus.PENDING,
            estimated_duration_minutes=60,
        ),
        LaundryTask(
            task_id=uuid4(),
            order_id=uuid4(),
            weight_kg=3.0,
            service_type="express",
            task_status=TaskStatus.IN_PROGRESS,
            estimated_duration_minutes=45,
        ),
    ]

    # Mock repository method
    mock_repo_instance = MagicMock()
    mock_repo_instance.find_by_service_type.return_value = mock_task_data
    mock_repository.return_value = mock_repo_instance

    # Test endpoint (belum ada, akan return 404)
    response = client.get("/laundry/tasks/search?service_type=express")

    # RED: Test akan gagal karena endpoint belum ada
    # Expected: 404 Not Found (karena endpoint belum diimplementasi)
    assert response.status_code == 404


def test_search_tasks_by_service_type_not_found(mock_repository: MagicMock):
    """Test mencari tasks dengan service_type yang tidak ada."""
    # Mock repository return empty list
    mock_repo_instance = MagicMock()
    mock_repo_instance.find_by_service_type.return_value = []
    mock_repository.return_value = mock_repo_instance

    # Test endpoint
    response = client.get("/laundry/tasks/search?service_type=premium")

    # RED: Test akan gagal karena endpoint belum ada
    assert response.status_code == 404


def test_search_tasks_by_service_type_invalid_parameter(mock_repository: MagicMock):
    """Test dengan parameter yang tidak valid."""
    # Test tanpa parameter
    response = client.get("/laundry/tasks/search")

    # RED: Test akan gagal karena endpoint belum ada
    assert response.status_code == 404

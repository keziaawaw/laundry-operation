"""
Unit tests for customers module.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from customers.api import router as customers_router

app = FastAPI()
app.include_router(customers_router, prefix="/customers")


class TestCustomersAPI:
    """Test cases for customers API endpoints."""

    def test_create_customer_without_auth(self, client):
        """Test creating customer without authentication."""
        customer = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+62812345678",
            "address": "Jl. Test No. 1",
            "city": "Jakarta",
            "postal_code": "12345",
        }
        response = client.post("/customers/customers", json=customer)
        assert response.status_code == 401

    def test_create_customer_with_auth(self, client, auth_headers):
        """Test creating customer with authentication."""
        customer = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+62812345678",
            "address": "Jl. Test No. 1",
            "city": "Jakarta",
            "postal_code": "12345",
        }
        response = client.post("/customers/customers", json=customer, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "John Doe"
        assert data["email"] == "john@example.com"
        assert data["phone"] == "+62812345678"
        assert "id" in data
        assert data["status"] == "active"
        assert "message" in data

    def test_create_customer_invalid_email(self, client, auth_headers):
        """Test creating customer with invalid email format."""
        customer = {
            "name": "John Doe",
            "email": "invalid-email",
            "phone": "+62812345678",
            "address": "Jl. Test No. 1",
            "city": "Jakarta",
            "postal_code": "12345",
        }
        response = client.post("/customers/customers", json=customer, headers=auth_headers)
        # Should return 422 validation error
        assert response.status_code == 422

    def test_get_customer_without_auth(self, client):
        """Test getting customer without authentication."""
        response = client.get("/customers/customers/cust_123")
        assert response.status_code == 401

    def test_get_customer_with_auth(self, client, auth_headers):
        """Test getting customer with authentication."""
        response = client.get("/customers/customers/cust_123", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "cust_123"
        assert "name" in data
        assert "email" in data
        assert "phone" in data
        assert "address" in data
        assert "city" in data
        assert "postal_code" in data
        assert "status" in data

    def test_get_customer_different_ids(self, client, auth_headers):
        """Test getting customer with different IDs."""
        customer_ids = ["cust_1", "cust_2", "cust_abc123"]

        for customer_id in customer_ids:
            response = client.get(f"/customers/customers/{customer_id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["id"] == customer_id

    def test_create_worker_without_auth(self, client):
        """Test creating worker without authentication."""
        worker = {"name": "Budi", "role": "washer", "phone": "+62812345679", "status": "available"}
        response = client.post("/customers/workers", json=worker)
        assert response.status_code == 401

    def test_create_worker_with_auth(self, client, auth_headers):
        """Test creating worker with authentication."""
        worker = {"name": "Budi", "role": "washer", "phone": "+62812345679", "status": "available"}
        response = client.post("/customers/workers", json=worker, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Budi"
        assert data["role"] == "washer"
        assert data["phone"] == "+62812345679"
        assert "id" in data
        assert "message" in data

    def test_create_worker_different_roles(self, client, auth_headers):
        """Test creating workers with different roles."""
        roles = ["picker", "washer", "ironer", "deliverer"]

        for role in roles:
            worker = {"name": f"Worker {role}", "role": role, "phone": "+62812345679", "status": "available"}
            response = client.post("/customers/workers", json=worker, headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["role"] == role

    def test_list_workers_without_auth(self, client):
        """Test listing workers without authentication."""
        response = client.get("/customers/workers")
        assert response.status_code == 401

    def test_list_workers_with_auth(self, client, auth_headers):
        """Test listing workers with authentication."""
        response = client.get("/customers/workers", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "workers" in data
        assert isinstance(data["workers"], list)
        assert len(data["workers"]) > 0
        assert "id" in data["workers"][0]
        assert "name" in data["workers"][0]
        assert "role" in data["workers"][0]

    def test_create_machine_without_auth(self, client):
        """Test creating machine without authentication."""
        machine = {"machine_type": "washer", "capacity_kg": 10.0, "status": "available", "location": "Room A"}
        response = client.post("/customers/machines", json=machine)
        assert response.status_code == 401

    def test_create_machine_with_auth(self, client, auth_headers):
        """Test creating machine with authentication."""
        machine = {"machine_type": "washer", "capacity_kg": 10.0, "status": "available", "location": "Room A"}
        response = client.post("/customers/machines", json=machine, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["machine_type"] == "washer"
        assert data["capacity_kg"] == 10.0
        assert data["status"] == "available"
        assert data["location"] == "Room A"
        assert "id" in data
        assert "message" in data

    def test_create_machine_different_types(self, client, auth_headers):
        """Test creating machines with different types."""
        machine_types = ["washer", "dryer", "ironer"]

        for machine_type in machine_types:
            machine = {
                "machine_type": machine_type,
                "capacity_kg": 8.0,
                "status": "available",
                "location": f"Room {machine_type}",
            }
            response = client.post("/customers/machines", json=machine, headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["machine_type"] == machine_type

    def test_list_machines_without_auth(self, client):
        """Test listing machines without authentication."""
        response = client.get("/customers/machines")
        assert response.status_code == 401

    def test_list_machines_with_auth(self, client, auth_headers):
        """Test listing machines with authentication."""
        response = client.get("/customers/machines", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "machines" in data
        assert isinstance(data["machines"], list)
        assert len(data["machines"]) > 0
        assert "id" in data["machines"][0]
        assert "machine_type" in data["machines"][0]
        assert "capacity_kg" in data["machines"][0]

"""
Unit tests for logistics module.
"""

import pytest
from datetime import datetime, timedelta
from logistics.api import router as logistics_router
from fastapi.testclient import TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(logistics_router, prefix="/logistics")


class TestLogisticsAPI:
    """Test cases for logistics API endpoints."""

    def test_schedule_pickup_without_auth(self, client):
        """Test scheduling pickup without authentication."""
        schedule = {
            "order_id": "order_123",
            "pickup_address": "Jl. Test No. 1",
            "delivery_address": "Jl. Test No. 2",
            "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "status": "pending",
        }
        response = client.post("/logistics/schedule-pickup", json=schedule)
        assert response.status_code == 401

    def test_schedule_pickup_with_auth(self, client, auth_headers):
        """Test scheduling pickup with authentication."""
        schedule = {
            "order_id": "order_123",
            "pickup_address": "Jl. Test No. 1",
            "delivery_address": "Jl. Test No. 2",
            "scheduled_time": (datetime.now() + timedelta(hours=2)).isoformat(),
            "status": "pending",
        }
        response = client.post("/logistics/schedule-pickup", json=schedule, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "order_123"
        assert data["status"] == "scheduled"
        assert data["pickup_address"] == "Jl. Test No. 1"
        assert "scheduled_time" in data
        assert "message" in data

    def test_schedule_pickup_with_courier_name(self, client, auth_headers):
        """Test scheduling pickup with courier name."""
        schedule = {
            "order_id": "order_456",
            "pickup_address": "Jl. Test No. 3",
            "delivery_address": "Jl. Test No. 4",
            "scheduled_time": (datetime.now() + timedelta(hours=1)).isoformat(),
            "courier_name": "John Doe",
            "status": "pending",
        }
        response = client.post("/logistics/schedule-pickup", json=schedule, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["order_id"] == "order_456"

    def test_schedule_delivery_without_auth(self, client):
        """Test scheduling delivery without authentication."""
        schedule = {
            "order_id": "order_123",
            "pickup_address": "Jl. Test No. 1",
            "delivery_address": "Jl. Test No. 2",
            "scheduled_time": (datetime.now() + timedelta(hours=3)).isoformat(),
        }
        response = client.post("/logistics/schedule-delivery", json=schedule)
        assert response.status_code == 401

    def test_schedule_delivery_with_auth(self, client, auth_headers):
        """Test scheduling delivery with authentication."""
        schedule = {
            "order_id": "order_789",
            "pickup_address": "Jl. Test No. 5",
            "delivery_address": "Jl. Test No. 6",
            "scheduled_time": (datetime.now() + timedelta(hours=3)).isoformat(),
        }
        response = client.post("/logistics/schedule-delivery", json=schedule, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "order_789"
        assert data["status"] == "scheduled"
        assert data["delivery_address"] == "Jl. Test No. 6"
        assert "message" in data

    def test_send_notification_without_auth(self, client):
        """Test sending notification without authentication."""
        notification = {
            "order_id": "order_123",
            "customer_phone": "+62812345678",
            "message_type": "pickup_reminder",
            "message_content": "Your pickup is scheduled",
        }
        response = client.post("/logistics/send-notification", json=notification)
        assert response.status_code == 401

    def test_send_notification_with_auth(self, client, auth_headers):
        """Test sending notification with authentication."""
        notification = {
            "order_id": "order_123",
            "customer_phone": "+62812345678",
            "message_type": "pickup_reminder",
            "message_content": "Your pickup is scheduled",
        }
        response = client.post("/logistics/send-notification", json=notification, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "order_123"
        assert data["message_type"] == "pickup_reminder"
        assert data["status"] == "sent"
        assert "timestamp" in data
        assert "message" in data

    def test_send_notification_different_types(self, client, auth_headers):
        """Test sending different types of notifications."""
        message_types = ["pickup_reminder", "on_the_way", "delivered"]

        for msg_type in message_types:
            notification = {
                "order_id": "order_123",
                "customer_phone": "+62812345678",
                "message_type": msg_type,
                "message_content": f"Message for {msg_type}",
            }
            response = client.post("/logistics/send-notification", json=notification, headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["message_type"] == msg_type

    def test_get_courier_location_without_auth(self, client):
        """Test getting courier location without authentication."""
        response = client.get("/logistics/courier-location/order_123")
        assert response.status_code == 401

    def test_get_courier_location_with_auth(self, client, auth_headers):
        """Test getting courier location with authentication."""
        response = client.get("/logistics/courier-location/order_123", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "order_123"
        assert "courier_name" in data
        assert "latitude" in data
        assert "longitude" in data
        assert "status" in data
        assert "eta_minutes" in data
        assert isinstance(data["latitude"], float)
        assert isinstance(data["longitude"], float)
        assert isinstance(data["eta_minutes"], int)

    def test_get_courier_location_different_orders(self, client, auth_headers):
        """Test getting courier location for different orders."""
        order_ids = ["order_1", "order_2", "order_abc123"]

        for order_id in order_ids:
            response = client.get(f"/logistics/courier-location/{order_id}", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["order_id"] == order_id

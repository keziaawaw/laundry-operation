"""
Unit tests for billing module.
"""

from datetime import datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from billing.api import router as billing_router

app = FastAPI()
app.include_router(billing_router, prefix="/billing")


class TestBillingAPI:
    """Test cases for billing API endpoints."""

    def test_calculate_cost_regular(self, client):
        """Test cost calculation for regular service."""
        response = client.post("/billing/calculate", json={"weight_kg": 5.0, "service_type": "regular", "note": None})
        assert response.status_code == 200
        data = response.json()
        assert data["weight_kg"] == 5.0
        assert data["service_type"] == "regular"
        assert data["base_rate"] == 5000
        assert data["multiplier"] == 1.0
        assert data["total_amount"] == 25000  # 5.0 * 5000 * 1.0
        assert data["currency"] == "IDR"

    def test_calculate_cost_express(self, client):
        """Test cost calculation for express service."""
        response = client.post("/billing/calculate", json={"weight_kg": 3.0, "service_type": "express"})
        assert response.status_code == 200
        data = response.json()
        assert data["multiplier"] == 1.5
        assert data["total_amount"] == 22500  # 3.0 * 5000 * 1.5

    def test_calculate_cost_delicate(self, client):
        """Test cost calculation for delicate service."""
        response = client.post("/billing/calculate", json={"weight_kg": 2.0, "service_type": "delicate"})
        assert response.status_code == 200
        data = response.json()
        assert data["multiplier"] == 1.2
        assert data["total_amount"] == 12000  # 2.0 * 5000 * 1.2

    def test_calculate_cost_unknown_service_type(self, client):
        """Test cost calculation with unknown service type (defaults to 1.0)."""
        response = client.post("/billing/calculate", json={"weight_kg": 4.0, "service_type": "unknown"})
        assert response.status_code == 200
        data = response.json()
        assert data["multiplier"] == 1.0
        assert data["total_amount"] == 20000  # 4.0 * 5000 * 1.0

    def test_calculate_cost_with_note(self, client):
        """Test cost calculation with note."""
        response = client.post(
            "/billing/calculate", json={"weight_kg": 5.0, "service_type": "regular", "note": "Handle with care"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_amount"] == 25000

    def test_calculate_cost_edge_cases(self, client):
        """Test cost calculation with edge cases."""
        # Zero weight
        response = client.post("/billing/calculate", json={"weight_kg": 0.0, "service_type": "regular"})
        assert response.status_code == 200
        assert response.json()["total_amount"] == 0

        # Very small weight
        response = client.post("/billing/calculate", json={"weight_kg": 0.1, "service_type": "regular"})
        assert response.status_code == 200
        assert response.json()["total_amount"] == 500  # 0.1 * 5000 * 1.0

        # Large weight
        response = client.post("/billing/calculate", json={"weight_kg": 100.0, "service_type": "express"})
        assert response.status_code == 200
        assert response.json()["total_amount"] == 750000  # 100.0 * 5000 * 1.5

    def test_payment_webhook(self, client):
        """Test payment webhook endpoint."""
        payload = {
            "transaction_id": "txn_123",
            "amount": 50000.0,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
        }
        response = client.post("/billing/payment/webhook", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["transaction_id"] == "txn_123"
        assert "message" in data

    def test_payment_webhook_different_statuses(self, client):
        """Test payment webhook with different payment statuses."""
        statuses = ["pending", "completed", "failed", "refunded"]

        for status in statuses:
            payload = {
                "transaction_id": f"txn_{status}",
                "amount": 50000.0,
                "status": status,
                "timestamp": datetime.now().isoformat(),
            }
            response = client.post("/billing/payment/webhook", json=payload)
            assert response.status_code == 200
            assert response.json()["transaction_id"] == f"txn_{status}"

    def test_get_payment_status(self, client):
        """Test getting payment status."""
        transaction_id = "txn_123"
        response = client.get(f"/billing/status/{transaction_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_id"] == transaction_id
        assert "status" in data
        assert "amount" in data
        assert "currency" in data

    def test_get_payment_status_different_ids(self, client):
        """Test getting payment status with different transaction IDs."""
        transaction_ids = ["txn_1", "txn_2", "txn_abc123", "txn_xyz"]

        for txn_id in transaction_ids:
            response = client.get(f"/billing/status/{txn_id}")
            assert response.status_code == 200
            assert response.json()["transaction_id"] == txn_id

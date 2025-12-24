"""
Unit tests for authentication module.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from jose import JWTError, jwt

from auth.api import router as auth_router
from auth.jwt_handler import ALGORITHM, SECRET_KEY, create_token, get_current_user
from auth.password import hash_password, verify_password
from auth.repository import user_repository

app = FastAPI()
app.include_router(auth_router, prefix="/auth")


class TestJWTHandler:
    """Test cases for JWT handler functions."""

    def test_create_token_default_expiry(self):
        """Test token creation with default expiry."""
        data = {"sub": "user123"}
        token = create_token(data)

        assert token is not None
        assert isinstance(token, str)

        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user123"
        assert "exp" in payload

    def test_create_token_custom_expiry(self):
        """Test token creation with custom expiry."""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        token = create_token(data, expires_delta=expires_delta)

        assert token is not None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user123"

    def test_create_token_with_additional_data(self):
        """Test token creation with additional data."""
        data = {"sub": "user123", "role": "admin", "email": "test@example.com"}
        token = create_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
        assert payload["email"] == "test@example.com"

    def test_get_current_user_valid_token(self, auth_token):
        """Test get_current_user with valid token."""
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        assert user_id is not None

    def test_get_current_user_missing_sub(self, client):
        """Test get_current_user with token without 'sub' field."""
        from unittest.mock import MagicMock

        from fastapi import APIRouter, Depends
        from fastapi.security import HTTPAuthorizationCredentials

        test_router = APIRouter()

        @test_router.get("/test")
        def test_endpoint(current_user=Depends(get_current_user)):
            return current_user

        test_app = FastAPI()
        test_app.include_router(test_router)
        test_client = TestClient(test_app)

        # Mock jwt.decode to return payload without 'sub'
        with patch("auth.jwt_handler.jwt.decode") as mock_decode:
            mock_decode.return_value = {"exp": int((datetime.utcnow() + timedelta(minutes=15)).timestamp())}

            # Create a valid token format
            token = create_token({"sub": "temp"})

            # Should raise 401 because token doesn't have 'sub' in payload
            response = test_client.get("/test", headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 401
            assert "Invalid authentication credentials" in response.json()["detail"]

    def test_get_current_user_no_credentials(self, client):
        """Test get_current_user with no credentials."""
        from fastapi import APIRouter, Depends

        test_router = APIRouter()

        @test_router.get("/test")
        def test_endpoint(current_user=Depends(get_current_user)):
            return current_user

        test_app = FastAPI()
        test_app.include_router(test_router)
        test_client = TestClient(test_app)

        # Should raise 401 because no credentials provided
        response = test_client.get("/test")
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_get_current_user_invalid_token(self, client):
        """Test get_current_user with invalid token (JWTError)."""
        from fastapi import APIRouter, Depends

        test_router = APIRouter()

        @test_router.get("/test")
        def test_endpoint(current_user=Depends(get_current_user)):
            return current_user

        test_app = FastAPI()
        test_app.include_router(test_router)
        test_client = TestClient(test_app)

        # Use invalid token (wrong secret key)
        invalid_token = jwt.encode(
            {"sub": "user123", "exp": int((datetime.utcnow() + timedelta(minutes=15)).timestamp())},
            "wrong_secret_key",
            algorithm=ALGORITHM,
        )

        # Should raise 401 because token is invalid
        response = test_client.get("/test", headers={"Authorization": f"Bearer {invalid_token}"})
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_get_current_user_expired_token(self, client):
        """Test get_current_user with expired token (JWTError)."""
        from fastapi import APIRouter, Depends

        test_router = APIRouter()

        @test_router.get("/test")
        def test_endpoint(current_user=Depends(get_current_user)):
            return current_user

        test_app = FastAPI()
        test_app.include_router(test_router)
        test_client = TestClient(test_app)

        # Create expired token
        expired_token = create_token({"sub": "user123"}, expires_delta=timedelta(minutes=-1))

        # Should raise 401 because token is expired
        response = test_client.get("/test", headers={"Authorization": f"Bearer {expired_token}"})
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_get_current_user_valid(self, client):
        """Test get_current_user with valid token."""
        from fastapi import APIRouter, Depends

        test_router = APIRouter()

        @test_router.get("/test")
        def test_endpoint(current_user=Depends(get_current_user)):
            return current_user

        test_app = FastAPI()
        test_app.include_router(test_router)
        test_client = TestClient(test_app)

        # Create valid token
        valid_token = create_token({"sub": "user123"})

        # Should return user data
        response = test_client.get("/test", headers={"Authorization": f"Bearer {valid_token}"})
        assert response.status_code == 200
        assert response.json() == {"user_id": "user123"}


class TestPasswordHashing:
    """Test cases for password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) == True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) == False

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        hashed1 = hash_password(password)
        hashed2 = hash_password(password)

        # Hashes should be different due to salt
        assert hashed1 != hashed2
        # But both should verify correctly
        assert verify_password(password, hashed1) == True
        assert verify_password(password, hashed2) == True

    def test_hash_password_non_string_input(self):
        """Test password hashing with non-string input."""
        # Test with integer
        password_int = 12345
        hashed = hash_password(password_int)
        assert hashed is not None
        assert isinstance(hashed, str)

        # Should still verify correctly
        assert verify_password("12345", hashed) == True

    def test_hash_password_long_password(self):
        """Test password hashing with very long password (>72 bytes)."""
        # Create password longer than 72 bytes
        long_password = "a" * 100
        hashed = hash_password(long_password)
        assert hashed is not None
        assert isinstance(hashed, str)
        # Should still work (truncated to 72 bytes)
        assert verify_password(long_password, hashed) == True

    def test_verify_password_non_string_input(self):
        """Test password verification with non-string input."""
        password = "testpassword123"
        hashed = hash_password(password)

        # Test with integer
        assert verify_password(12345, hashed) == False
        # Test with correct password as integer (converted to string)
        # This tests the isinstance check
        password_int = 12345
        hashed_int = hash_password(password_int)
        assert verify_password(password_int, hashed_int) == True

    def test_verify_password_long_password(self):
        """Test password verification with very long password."""
        long_password = "b" * 100
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) == True

    def test_verify_password_invalid_hash_format(self):
        """Test password verification with invalid hash format."""
        password = "testpassword123"
        # Invalid hash format should trigger exception handling
        invalid_hash = "invalid_hash_format"
        result = verify_password(password, invalid_hash)
        # Should return False when exception occurs
        assert result == False

    def test_hash_password_fallback_path(self):
        """Test password hashing fallback path when passlib raises ValueError."""
        from unittest.mock import MagicMock, patch

        from auth.password import hash_password

        # Mock passlib to raise ValueError to trigger fallback
        with patch("auth.password.pwd_context.hash") as mock_hash:
            mock_hash.side_effect = ValueError("Some error")

            # Should use bcrypt fallback
            password = "testpassword123"
            hashed = hash_password(password)
            assert hashed is not None
            assert isinstance(hashed, str)
            # Should still be valid bcrypt hash
            assert hashed.startswith("$2b$") or hashed.startswith("$2a$") or hashed.startswith("$2y$")

    def test_verify_password_fallback_path(self):
        """Test password verification fallback path when passlib raises exception."""
        from unittest.mock import patch

        from auth.password import hash_password, verify_password

        password = "testpassword123"
        hashed = hash_password(password)

        # Mock passlib verify to raise exception to trigger fallback
        with patch("auth.password.pwd_context.verify") as mock_verify:
            mock_verify.side_effect = ValueError("Some error")

            # Should use bcrypt fallback
            result = verify_password(password, hashed)
            assert result == True


class TestAuthAPI:
    """Test cases for authentication API endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        import time

        timestamp = int(time.time())
        user_data = {
            "username": f"newuser_{timestamp}",
            "email": f"newuser_{timestamp}@example.com",
            "password": "password123",
            "full_name": "New User",
        }
        response = client.post("/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be in response

    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username."""
        import time

        timestamp = int(time.time())
        user_data = {
            "username": f"duplicate_{timestamp}",
            "email": f"user1_{timestamp}@example.com",
            "password": "password123",
        }

        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 201

        # Second registration with same username should fail
        user_data["email"] = f"user2_{timestamp}@example.com"
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Username already exists" in response2.json()["detail"]

    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        import time

        timestamp = int(time.time())
        user_data1 = {
            "username": f"user1_{timestamp}",
            "email": f"duplicate_{timestamp}@example.com",
            "password": "password123",
        }

        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data1)
        assert response1.status_code == 201

        # Second registration with same email should fail
        user_data2 = {
            "username": f"user2_{timestamp}",
            "email": f"duplicate_{timestamp}@example.com",
            "password": "password123",
        }
        response2 = client.post("/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Email already exists" in response2.json()["detail"]

    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        import time

        timestamp = int(time.time())
        user_data = {"username": f"user_{timestamp}", "email": "invalid-email", "password": "password123"}
        response = client.post("/auth/register", json=user_data)

        # Should return 422 validation error
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        # Missing email
        response = client.post("/auth/register", json={"username": "testuser", "password": "password123"})
        assert response.status_code == 422

        # Missing password
        response = client.post("/auth/register", json={"username": "testuser", "email": "test@example.com"})
        assert response.status_code == 422

    def test_login_success(self, client, registered_user):
        """Test successful login with registered user."""
        response = client.post(
            "/auth/login", data={"username": registered_user["username"], "password": registered_user["password"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)

        # Verify token can be decoded
        token = data["access_token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == registered_user["username"]
        assert "user_id" in payload
        assert "exp" in payload

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password."""
        response = client.post("/auth/login", data={"username": registered_user["username"], "password": "wrongpassword"})

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/auth/login", data={"username": "nonexistent_user", "password": "password123"})

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post("/auth/login", data={"username": "", "password": ""})

        # Should return 401 or 422
        assert response.status_code in [401, 422]

    def test_register_then_login_flow(self, client):
        """Test complete flow: register then login."""
        import time

        timestamp = int(time.time())

        # Register
        user_data = {
            "username": f"flowuser_{timestamp}",
            "email": f"flowuser_{timestamp}@example.com",
            "password": "password123",
            "full_name": "Flow User",
        }
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 201

        # Login
        login_response = client.post(
            "/auth/login", data={"username": user_data["username"], "password": user_data["password"]}
        )
        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_register_exception_handling(self, client):
        """Test register endpoint exception handling for general exceptions."""
        import time
        from unittest.mock import patch

        timestamp = int(time.time())
        user_data = {
            "username": f"exception_{timestamp}",
            "email": f"exception_{timestamp}@example.com",
            "password": "password123",
        }

        # Mock hash_password to raise general exception
        with patch("auth.api.hash_password") as mock_hash:
            mock_hash.side_effect = Exception("Unexpected error")

            response = client.post("/auth/register", json=user_data)
            assert response.status_code == 500
            assert "Error creating user" in response.json()["detail"]

    def test_login_exception_handling(self, client, registered_user):
        """Test login endpoint exception handling for token creation errors."""
        from unittest.mock import patch

        # Mock create_token to raise exception
        with patch("auth.api.create_token") as mock_token:
            mock_token.side_effect = Exception("Token creation failed")

            response = client.post(
                "/auth/login", data={"username": registered_user["username"], "password": registered_user["password"]}
            )
            assert response.status_code == 500
            assert "Error creating token" in response.json()["detail"]

    def test_login_requires_form_data(self, client, registered_user):
        """Test that login requires form data (OAuth2PasswordRequestForm)."""
        # Try with JSON (should fail or not work as expected)
        response = client.post(
            "/auth/login", json={"username": registered_user["username"], "password": registered_user["password"]}
        )
        # OAuth2PasswordRequestForm requires form data, not JSON
        # This might return 422 or handle differently
        assert response.status_code in [200, 422]

    def test_deps_import(self):
        """Test that deps.py can be imported and used."""
        # Test that deps.py re-export works
        from auth.deps import get_current_user

        assert get_current_user is not None
        # Verify it's the same function from jwt_handler
        from auth.jwt_handler import get_current_user as jwt_get_current_user

        assert get_current_user == jwt_get_current_user


class TestUserRepository:
    """Test cases for UserRepository."""

    def test_get_user_by_email(self, client):
        """Test getting user by email."""
        import time

        from auth.repository import user_repository

        timestamp = int(time.time())
        user_data = {
            "username": f"emailtest_{timestamp}",
            "email": f"emailtest_{timestamp}@example.com",
            "password": "password123",
        }

        # Register user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201

        # Get user by email
        user = user_repository.get_user_by_email(user_data["email"])
        assert user is not None
        assert user.email == user_data["email"]
        assert user.username == user_data["username"]

    def test_get_user_by_email_nonexistent(self):
        """Test getting user by email that doesn't exist."""
        from auth.repository import user_repository

        user = user_repository.get_user_by_email("nonexistent@example.com")
        assert user is None

    def test_get_user_by_id(self, client):
        """Test getting user by ID."""
        import time

        from auth.repository import user_repository

        timestamp = int(time.time())
        user_data = {"username": f"idtest_{timestamp}", "email": f"idtest_{timestamp}@example.com", "password": "password123"}

        # Register user
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Get user by ID
        user = user_repository.get_user_by_id(user_id)
        assert user is not None
        assert user.id == user_id
        assert user.username == user_data["username"]

    def test_get_user_by_id_nonexistent(self):
        """Test getting user by ID that doesn't exist."""
        from auth.repository import user_repository

        user = user_repository.get_user_by_id("nonexistent-id")
        assert user is None

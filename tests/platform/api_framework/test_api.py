"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from psyai.platform.api_framework.app import create_app
from psyai.platform.api_framework.auth import get_password_hash
from psyai.platform.storage_layer import Base, User, get_db


# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Create test client."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create app
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    # Create client
    with TestClient(app) as test_client:
        yield test_client

    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(client):
    """Create a test user."""
    db = TestingSessionLocal()

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_expert=False,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    yield user

    db.close()


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "testpassword123"},
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_health_check(self, client):
        """Test basic health check."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_ping(self, client):
        """Test ping endpoint."""
        response = client.get("/api/v1/ping")

        assert response.status_code == 200
        assert response.json() == {"message": "pong"}


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # Already exists
                "username": "differentuser",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "test@example.com", "password": "wrongpassword"},
        )

        assert response.status_code == 401

    def test_login_json(self, client, test_user):
        """Test JSON login."""
        response = client.post(
            "/api/v1/auth/login/json",
            json={"email": "test@example.com", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestUserEndpoints:
    """Test user endpoints."""

    def test_get_current_user(self, client, test_user, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/users/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth."""
        response = client.get("/api/v1/users/me")

        assert response.status_code == 401

    def test_update_current_user(self, client, test_user, auth_headers):
        """Test updating current user."""
        response = client.put(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"full_name": "Updated Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    def test_get_user_by_id(self, client, test_user, auth_headers):
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id


class TestChatEndpoints:
    """Test chat endpoints."""

    def test_create_chat_session(self, client, test_user, auth_headers):
        """Test creating a chat session."""
        response = client.post(
            "/api/v1/chat/sessions",
            headers=auth_headers,
            json={"mode": "ai", "title": "Test Session"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["mode"] == "ai"
        assert data["title"] == "Test Session"
        assert data["user_id"] == test_user.id

    def test_list_chat_sessions(self, client, test_user, auth_headers):
        """Test listing chat sessions."""
        # Create a session first
        client.post(
            "/api/v1/chat/sessions",
            headers=auth_headers,
            json={"mode": "ai"},
        )

        response = client.get("/api/v1/chat/sessions", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_send_message(self, client, test_user, auth_headers):
        """Test sending a message."""
        # Create session
        session_response = client.post(
            "/api/v1/chat/sessions",
            headers=auth_headers,
            json={"mode": "ai"},
        )
        session_id = session_response.json()["id"]

        # Send message
        response = client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"content": "Hello, world!"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Hello, world!"
        assert data["role"] == "user"

    def test_get_session_messages(self, client, test_user, auth_headers):
        """Test getting session messages."""
        # Create session
        session_response = client.post(
            "/api/v1/chat/sessions",
            headers=auth_headers,
            json={"mode": "ai"},
        )
        session_id = session_response.json()["id"]

        # Send message
        client.post(
            f"/api/v1/chat/sessions/{session_id}/messages",
            headers=auth_headers,
            json={"content": "Test message"},
        )

        # Get messages
        response = client.get(
            f"/api/v1/chat/sessions/{session_id}/messages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["content"] == "Test message"

"""Smoke tests to verify basic application functionality."""
import pytest


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_current_principal(auth_client):
    """Test GET /auth/me endpoint."""
    response = auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "role" in data
    assert "display_name" in data
    assert "scopes" in data
    assert isinstance(data["scopes"], list)


def test_database_session(db_session):
    """Test that database session is functional."""
    from app.models import User
    
    # Create a test user
    test_user = User(
        id="test-user-id",
        external_subject="test@example.com",
        role_code="operations",
        display_name="Test User",
        active_flag=True,
    )
    db_session.add(test_user)
    db_session.commit()
    
    # Query the user back
    retrieved = db_session.query(User).filter(User.id == "test-user-id").first()
    assert retrieved is not None
    assert retrieved.display_name == "Test User"

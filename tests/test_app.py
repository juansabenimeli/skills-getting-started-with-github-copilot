import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()

    # Check that we have activities
    assert isinstance(data, dict)
    assert len(data) > 0

    # Check structure of first activity
    first_activity = next(iter(data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    # Use an activity that exists and a new email
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    """Test signup when student is already signed up"""
    # First signup
    client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")

    # Try to signup again
    response = client.post("/activities/Tennis%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up for this activity" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Basketball%20Team/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Basketball Team" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Basketball Team"]["participants"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/NonExistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    """Test unregister when student is not signed up"""
    response = client.delete("/activities/Drama%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up for this activity" in data["detail"]
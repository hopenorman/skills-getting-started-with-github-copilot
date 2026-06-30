import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as school_app

client = TestClient(school_app.app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(school_app.activities)
    yield
    school_app.activities.clear()
    school_app.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = "testuser@mergington.edu"
    activity_name = quote("Chess Club", safe="")
    url = f"/activities/{activity_name}/signup"
    assert email not in school_app.activities["Chess Club"]["participants"]

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in school_app.activities["Chess Club"]["participants"]


def test_signup_for_activity_fails_when_duplicate():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = quote("Chess Club", safe="")
    url = f"/activities/{activity_name}/signup"
    assert email in school_app.activities["Chess Club"]["participants"]

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404():
    # Arrange
    email = "testuser@mergington.edu"
    activity_name = quote("Nonexistent Club", safe="")
    url = f"/activities/{activity_name}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_activity_participant_removes_existing_participant():
    # Arrange
    email = "alex@mergington.edu"
    activity_name = quote("Basketball Team", safe="")
    url = f"/activities/{activity_name}/signup"
    assert email in school_app.activities["Basketball Team"]["participants"]

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Basketball Team"}
    assert email not in school_app.activities["Basketball Team"]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    email = "missing@mergington.edu"
    activity_name = quote("Basketball Team", safe="")
    url = f"/activities/{activity_name}/signup"
    assert email not in school_app.activities["Basketball Team"]["participants"]

    # Act
    response = client.delete(url, params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"

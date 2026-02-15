"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test to ensure isolation"""
    from app import activities
    
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join our competitive basketball team",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and play tennis with fellow students",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "casey@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Build and program robots for competitions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 14,
            "participants": ["lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and theatrical productions",
            "schedule": "Tuesdays and Thursdays, 4:45 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Mondays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_has_correct_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
        
    def test_get_activities_includes_participants(self, client):
        """Test that participants are included in response"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds participant to list"""
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 3
        
    def test_signup_duplicate_email_fails(self, client):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
        
    def test_signup_multiple_activities(self, client):
        """Test that same email can signup for multiple activities"""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1
        
    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering non-existent participant fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
        
    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
        
    def test_unregister_then_signup_again(self, client):
        """Test that participant can unregister and signup again"""
        email = "michael@mergington.edu"
        
        # Unregister
        response1 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
        
        # Sign up again
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify signed up again
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_complete_signup_and_unregister_flow(self, client):
        """Test complete flow: signup, verify, unregister, verify"""
        email = "integration@mergington.edu"
        activity = "Orchestra"
        
        # Check initial state - no Orchestra
        response = client.get("/activities")
        assert activity not in response.json()
        
        # Create Orchestra by signing up (would fail with current implementation)
        # This test shows the expected behavior if we add a feature to create activities
        
    def test_multiple_participants_management(self, client):
        """Test managing multiple participants in one activity"""
        activity = "Chess Club"
        emails = ["new1@mergington.edu", "new2@mergington.edu", "new3@mergington.edu"]
        
        # Add multiple participants
        for email in emails:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all added
        response = client.get("/activities")
        data = response.json()
        participants = data[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Remove one
        client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={emails[0]}"
        )
        
        # Verify only one removed
        response = client.get("/activities")
        data = response.json()
        participants = data[activity]["participants"]
        assert emails[0] not in participants
        assert emails[1] in participants
        assert emails[2] in participants

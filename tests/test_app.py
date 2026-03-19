"""
Tests for the Mergington High School Activity Management API
Using the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        # Arrange
        # (No setup needed, activities are already in the app)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
    def test_get_activities_has_required_fields(self, client):
        """Test that activities contain required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"Missing {field} in {activity_name}"
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Arrange
        test_email = "new_student@mergington.edu"
        test_activity = "Chess Club"
        
        # Act
        response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert test_email in activities_response.json()[test_activity]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        # Arrange
        test_email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client):
        """Test that a student cannot register twice for the same activity"""
        # Arrange
        test_email = "duplicate_check@mergington.edu"
        test_activity = "Programming Class"
        
        # Act - First signup
        first_response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert first signup succeeds
        assert first_response.status_code == 200
        
        # Act - Second signup (duplicate attempt)
        second_response = client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Assert second signup fails
        assert second_response.status_code == 400
        assert "already" in second_response.json()["detail"].lower()
    
    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        # Arrange
        test_activity = "Gym Class"
        test_emails = ["multi_student1@test.com", "multi_student2@test.com", "multi_student3@test.com"]
        
        # Act
        for email in test_emails:
            response = client.post(
                f"/activities/{test_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert - Verify all students are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()[test_activity]["participants"]
        for email in test_emails:
            assert email in participants


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant"""
        # Arrange
        test_email = "remove_me@mergington.edu"
        test_activity = "Tennis Club"
        
        # First, sign up the participant
        client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{test_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was actually removed
        activities_response = client.get("/activities")
        assert test_email not in activities_response.json()[test_activity]["participants"]
    
    def test_remove_participant_activity_not_found(self, client):
        """Test removing participant from non-existent activity"""
        # Arrange
        test_email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_participant_not_found(self, client):
        """Test removing non-existent participant from activity"""
        # Arrange
        test_email = "ghost@mergington.edu"
        test_activity = "Chess Club"
        
        # Act
        response = client.delete(
            f"/activities/{test_activity}/participants/{test_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_participant_twice(self, client):
        """Test that removing a participant twice fails on second attempt"""
        # Arrange
        test_email = "double_remove@mergington.edu"
        test_activity = "Science Club"
        
        # Sign up the participant
        client.post(
            f"/activities/{test_activity}/signup",
            params={"email": test_email}
        )
        
        # Act - First removal
        first_response = client.delete(
            f"/activities/{test_activity}/participants/{test_email}"
        )
        
        # Assert first removal succeeds
        assert first_response.status_code == 200
        
        # Act - Second removal attempt
        second_response = client.delete(
            f"/activities/{test_activity}/participants/{test_email}"
        )
        
        # Assert second removal fails
        assert second_response.status_code == 400

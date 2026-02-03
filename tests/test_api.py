"""Tests for API endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns 200."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data


class TestConversationEndpoint:
    """Tests for the conversation endpoint."""

    def test_create_conversation(self, client, api_key_headers):
        """Test creating a new conversation."""
        response = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversation_id" in data

    def test_process_message_with_valid_api_key(self, client, api_key_headers, sample_scam_message):
        """Test processing a message with valid API key."""
        response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=sample_scam_message,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "response" in data
        assert "scam_detected" in data
        assert "extracted_intelligence" in data

    def test_process_message_without_api_key(self, client, sample_scam_message):
        """Test processing a message without API key returns 401."""
        response = client.post(
            "/api/v1/conversation/message",
            json=sample_scam_message,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_process_message_with_invalid_api_key(self, client, sample_scam_message):
        """Test processing a message with invalid API key returns 403."""
        response = client.post(
            "/api/v1/conversation/message",
            headers={"Authorization": "Bearer invalid_key"},
            json=sample_scam_message,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_conversation(self, client, api_key_headers):
        """Test retrieving conversation history."""
        # First create a conversation
        create_response = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        )
        conv_id = create_response.json()["conversation_id"]

        # Then retrieve it
        response = client.get(
            f"/api/v1/conversation/{conv_id}",
            headers=api_key_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["conversation_id"] == conv_id
        assert "messages" in data

    def test_get_nonexistent_conversation(self, client, api_key_headers):
        """Test retrieving non-existent conversation returns 404."""
        response = client.get(
            "/api/v1/conversation/nonexistent-id",
            headers=api_key_headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

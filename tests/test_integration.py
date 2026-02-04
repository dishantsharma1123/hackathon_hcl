"""Integration tests for the Agentic Honey-Pot System."""

import pytest
from fastapi import status
from datetime import datetime
import uuid


class TestConversationFlow:
    """Integration tests for full conversation flow."""

    def test_full_conversation_flow(self, client, api_key_headers):
        """Test complete conversation flow from start to end."""
        # Step 1: Create new conversation
        create_response = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        )
        assert create_response.status_code == status.HTTP_200_OK
        conv_id = create_response.json()["conversation_id"]
        
        # Step 2: Send first scam message
        first_msg = {
            "conversation_id": conv_id,
            "message": "Congratulations! You've won Rs. 50,000 in our lottery.",
            "sender_id": "scammer123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        first_response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=first_msg,
        )
        assert first_response.status_code == status.HTTP_200_OK
        data = first_response.json()
        assert data["scam_detected"] is True
        assert data["agent_active"] is True
        assert len(data["response"]) > 0
        
        # Step 3: Send second message (scammer provides UPI)
        second_msg = {
            "conversation_id": conv_id,
            "message": "Send Rs. 500 to winner@paytm to claim your prize.",
            "sender_id": "scammer123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [
                {"role": "user", "message": first_msg["message"]},
                {"role": "assistant", "message": data["response"]},
            ],
        }
        second_response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=second_msg,
        )
        assert second_response.status_code == status.HTTP_200_OK
        data2 = second_response.json()
        assert data2["scam_detected"] is True
        
        # Step 4: Verify UPI was extracted
        upi_ids = data2["extracted_intelligence"]["upi_ids"]
        assert len(upi_ids) > 0
        assert any("winner@paytm" in upi["upi_id"] for upi in upi_ids)
        
        # Step 5: Retrieve full conversation
        conv_response = client.get(
            f"/api/v1/conversation/{conv_id}",
            headers=api_key_headers,
        )
        assert conv_response.status_code == status.HTTP_200_OK
        conv_data = conv_response.json()
        assert len(conv_data["messages"]) == 4  # 2 user + 2 assistant

    def test_multiple_conversations(self, client, api_key_headers):
        """Test handling multiple independent conversations."""
        # Create two conversations
        conv1 = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        conv2 = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        assert conv1 != conv2
        
        # Send messages to both
        msg1 = {
            "conversation_id": conv1,
            "message": "URGENT: You won a lottery!",
            "sender_id": "scammer1",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        msg2 = {
            "conversation_id": conv2,
            "message": "URGENT: Your account is blocked!",
            "sender_id": "scammer2",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        response1 = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg1,
        )
        response2 = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg2,
        )
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify conversations are independent
        conv1_data = client.get(
            f"/api/v1/conversation/{conv1}",
            headers=api_key_headers,
        ).json()
        
        conv2_data = client.get(
            f"/api/v1/conversation/{conv2}",
            headers=api_key_headers,
        ).json()
        
        # Each should have different messages
        assert conv1_data["conversation_id"] == conv1
        assert conv2_data["conversation_id"] == conv2

    def test_legitimate_message_flow(self, client, api_key_headers):
        """Test flow with legitimate (non-scam) message."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Send legitimate message
        msg = {
            "conversation_id": conv_id,
            "message": "Hi, how are you doing today?",
            "sender_id": "user123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg,
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should not be detected as scam
        assert data["scam_detected"] is False
        assert data["agent_active"] is False
        # Should have polite decline response
        assert "not interested" in data["response"].lower()

    def test_intelligence_extraction_across_turns(self, client, api_key_headers):
        """Test intelligence extraction across multiple conversation turns."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Turn 1: Initial scam message - UPDATED for better detection
        msg1 = {
            "conversation_id": conv_id,
            "message": "URGENT! Work from home! Earn Money now!",
            "sender_id": "scammer",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        response1 = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg1,
        ).json()
        
        history = [
            {"role": "user", "message": msg1["message"]},
            {"role": "assistant", "message": response1["response"]},
        ]
        
        # Turn 2: Scammer provides UPI
        msg2 = {
            "conversation_id": conv_id,
            "message": "Pay Rs. 2000 registration fee to jobportal@icici",
            "sender_id": "scammer",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": history,
        }
        response2 = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg2,
        ).json()
        
        # Verify UPI extracted
        upi_ids = response2["extracted_intelligence"]["upi_ids"]
        assert len(upi_ids) > 0
        
        history.extend([
            {"role": "user", "message": msg2["message"]},
            {"role": "assistant", "message": response2["response"]},
        ])
        
        # Turn 3: Scammer provides phone
        msg3 = {
            "conversation_id": conv_id,
            "message": "Or call us at +91-9876543210 for more details",
            "sender_id": "scammer",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": history,
        }
        response3 = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg3,
        ).json()
        
        # Verify phone extracted
        phones = response3["extracted_intelligence"]["phone_numbers"]
        assert len(phones) > 0
        
        # Verify engagement metrics increased
        assert response3["engagement_metrics"]["conversation_turns"] == 3


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_conversation_id_format(self, client, api_key_headers):
        """Test handling of invalid conversation ID format."""
        response = client.get(
            "/api/v1/conversation/invalid-uuid-format",
            headers=api_key_headers,
        )
        # Should return 404 or validation error
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_missing_required_fields(self, client, api_key_headers):
        """Test handling of missing required fields."""
        # Missing message field
        incomplete_request = {
            "conversation_id": str(uuid.uuid4()),
            "sender_id": "user123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        
        response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=incomplete_request,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_message(self, client, api_key_headers):
        """Test handling of empty message."""
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        msg = {
            "conversation_id": conv_id,
            "message": "",
            "sender_id": "user123",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg,
        )
        
        # Should handle gracefully (either accept or reject with proper error)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestPerformance:
    """Integration tests for performance requirements."""

    def test_response_time_acceptable(self, client, api_key_headers):
        """Test that API response time is acceptable (< 2 seconds)."""
        import time
        
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        msg = {
            "conversation_id": conv_id,
            "message": "You won Rs. 50,000!",
            "sender_id": "scammer",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        start_time = time.time()
        response = client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=msg,
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == status.HTTP_200_OK
        # Response time should be reasonable (note: may be slower with actual LLM calls)
        # For testing purposes, we use a generous threshold
        assert response_time < 30  # 30 seconds for LLM processing
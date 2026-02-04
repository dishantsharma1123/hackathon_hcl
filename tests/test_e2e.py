"""End-to-end tests for the Agentic Honey-Pot System."""

import pytest
import time
from fastapi import status
from datetime import datetime
import httpx


class TestE2EScenarioLotteryScam:
    """E2E test for lottery scam scenario."""

    def test_lottery_scam_complete_flow(self, client, api_key_headers):
        """Test complete lottery scam flow from detection to intelligence extraction."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Scenario: Scammer sends lottery win message
        scammer_messages = [
            "Congratulations! You've won Rs. 50,000 in our lucky draw!",
            "To claim, you need to pay a processing fee of Rs. 500.",
            "Send the fee to this UPI ID: winner@paytm",
            "After payment, we will transfer Rs. 50,000 to your account.",
        ]
        
        conversation_history = []
        extracted_upi = False
        
        for i, scammer_msg in enumerate(scammer_messages):
            # Send scammer message
            request = {
                "conversation_id": conv_id,
                "message": scammer_msg,
                "sender_id": "scammer_lottery",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_history": conversation_history.copy(),
            }
            
            response = client.post(
                "/api/v1/conversation/message",
                headers=api_key_headers,
                json=request,
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify scam is detected
            assert data["scam_detected"] is True
            assert data["agent_active"] is True
            
            # Check for UPI extraction
            upi_ids = data["extracted_intelligence"]["upi_ids"]
            if upi_ids:
                extracted_upi = True
                assert any("winner@paytm" in upi["upi_id"] for upi in upi_ids)
            
            # Add to history
            conversation_history.append({
                "role": "user",
                "message": scammer_msg,
            })
            conversation_history.append({
                "role": "assistant",
                "message": data["response"],
            })
            
            # Verify agent responds naturally
            assert len(data["response"]) > 0
            assert data["response"] != scammer_msg  # Not echoing
        
        # Final verification: UPI should be extracted
        assert extracted_upi is True, "UPI ID should be extracted by end of conversation"
        
        # Verify conversation is saved
        conv_data = client.get(
            f"/api/v1/conversation/{conv_id}",
            headers=api_key_headers,
        ).json()
        
        assert conv_data["scam_detected"] is True
        assert conv_data["agent_active"] is True
        assert len(conv_data["messages"]) > 0


class TestE2EScenarioPhishingScam:
    """E2E test for phishing scam scenario."""

    def test_phishing_scam_complete_flow(self, client, api_key_headers):
        """Test complete phishing scam flow."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Scenario: Bank phishing scam
        scammer_messages = [
            "Your bank account will be blocked due to KYC non-compliance.",
            "Please update your KYC details immediately.",
            "Click this link to verify: http://secure-bank-verify.com/login",
            "Enter your account number and password on the secure page.",
        ]
        
        conversation_history = []
        extracted_url = False
        
        for scammer_msg in scammer_messages:
            request = {
                "conversation_id": conv_id,
                "message": scammer_msg,
                "sender_id": "scammer_phishing",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_history": conversation_history.copy(),
            }
            
            response = client.post(
                "/api/v1/conversation/message",
                headers=api_key_headers,
                json=request,
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Check for phishing URL extraction
            urls = data["extracted_intelligence"]["phishing_urls"]
            if urls:
                extracted_url = True
                assert any("secure-bank-verify.com" in url["domain"] for url in urls)
            
            conversation_history.append({
                "role": "user",
                "message": scammer_msg,
            })
            conversation_history.append({
                "role": "assistant",
                "message": data["response"],
            })
        
        # Verify URL was extracted
        assert extracted_url is True, "Phishing URL should be extracted"


class TestE2EScenarioJobScam:
    """E2E test for job scam scenario."""

    def test_job_scam_complete_flow(self, client, api_key_headers):
        """Test complete job scam flow."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Scenario: Work from home job scam
        scammer_messages = [
            "Work from home! Earn Rs. 30,000 to Rs. 50,000 per month.",
            "No experience required. Flexible hours.",
            "Pay Rs. 2000 registration fee to get started.",
            "Send payment to jobportal@icici to activate your account.",
            "You can also call us at +91-9876543210 for queries.",
        ]
        
        conversation_history = []
        extracted_upi = False
        extracted_phone = False
        
        for scammer_msg in scammer_messages:
            request = {
                "conversation_id": conv_id,
                "message": scammer_msg,
                "sender_id": "scammer_job",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_history": conversation_history.copy(),
            }
            
            response = client.post(
                "/api/v1/conversation/message",
                headers=api_key_headers,
                json=request,
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Check for UPI extraction
            upi_ids = data["extracted_intelligence"]["upi_ids"]
            if upi_ids and not extracted_upi:
                extracted_upi = True
                assert any("jobportal@icici" in upi["upi_id"] for upi in upi_ids)
            
            # Check for phone extraction
            phones = data["extracted_intelligence"]["phone_numbers"]
            if phones and not extracted_phone:
                extracted_phone = True
                assert any("9876543210" in phone["number"] for phone in phones)
            
            conversation_history.append({
                "role": "user",
                "message": scammer_msg,
            })
            conversation_history.append({
                "role": "assistant",
                "message": data["response"],
            })
        
        # Verify both UPI and phone were extracted
        assert extracted_upi is True, "UPI ID should be extracted"
        assert extracted_phone is True, "Phone number should be extracted"


class TestE2EScenarioLegitimateConversation:
    """E2E test for legitimate (non-scam) conversation."""

    def test_legitimate_conversation_flow(self, client, api_key_headers):
        """Test that legitimate messages are handled correctly."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Scenario: Normal conversation
        messages = [
            "Hi, I'm interested in your product.",
            "What are the specifications?",
            "How much does it cost?",
            "Can I get a discount?",
        ]
        
        conversation_history = []
        
        for msg in messages:
            request = {
                "conversation_id": conv_id,
                "message": msg,
                "sender_id": "customer",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_history": conversation_history.copy(),
            }
            
            response = client.post(
                "/api/v1/conversation/message",
                headers=api_key_headers,
                json=request,
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Should not be detected as scam
            assert data["scam_detected"] is False
            assert data["agent_active"] is False
            
            # Should have polite decline or neutral response
            assert len(data["response"]) > 0
            
            conversation_history.append({
                "role": "user",
                "message": msg,
            })
            conversation_history.append({
                "role": "assistant",
                "message": data["response"],
            })


class TestE2EPerformanceAndReliability:
    """E2E tests for performance and reliability."""

    def test_concurrent_conversations(self, client, api_key_headers):
        """Test handling multiple concurrent conversations."""
        import threading
        
        results = []
        
        def process_conversation(conv_num):
            """Process a single conversation in a thread."""
            try:
                conv_id = client.post(
                    "/api/v1/conversation/new",
                    headers=api_key_headers,
                ).json()["conversation_id"]
                
                # UPDATED: Use a clear scam message to ensure detection
                request = {
                    "conversation_id": conv_id,
                    "message": f"URGENT: You won a lottery! Claim now {conv_num}",
                    "sender_id": f"scammer_{conv_num}",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "conversation_history": [],
                }
                
                response = client.post(
                    "/api/v1/conversation/message",
                    headers=api_key_headers,
                    json=request,
                )
                
                results.append({
                    "conv_num": conv_num,
                    "status": response.status_code,
                    "success": response.status_code == status.HTTP_200_OK,
                })
            except Exception as e:
                results.append({
                    "conv_num": conv_num,
                    "status": 500,
                    "success": False,
                    "error": str(e),
                })
        
        # Create 5 concurrent conversations
        threads = []
        for i in range(5):
            thread = threading.Thread(target=process_conversation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=60)
        
        # Verify all conversations succeeded
        assert len(results) == 5
        assert all(r["success"] for r in results), \
            f"Some conversations failed: {results}"

    def test_long_conversation_turns(self, client, api_key_headers):
        """Test that system handles long conversations."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        conversation_history = []
        max_turns = 10  # Test with 10 turns
        
        for turn in range(max_turns):
            # UPDATED: Use a clear scam message to ensure the agent stays active
            request = {
                "conversation_id": conv_id,
                "message": f"URGENT: You have won a lottery prize of Rs. {turn}000! Click here.",
                "sender_id": "scammer",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "conversation_history": conversation_history.copy(),
            }
            
            response = client.post(
                "/api/v1/conversation/message",
                headers=api_key_headers,
                json=request,
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            # Verify engagement metrics
            assert data["engagement_metrics"]["conversation_turns"] == turn + 1
            
            conversation_history.append({
                "role": "user",
                "message": request["message"],
            })
            conversation_history.append({
                "role": "assistant",
                "message": data["response"],
            })
        
        # Final verification
        conv_data = client.get(
            f"/api/v1/conversation/{conv_id}",
            headers=api_key_headers,
        ).json()
        
        assert len(conv_data["messages"]) == max_turns * 2  # Each turn has 2 messages


class TestE2EDataPersistence:
    """E2E tests for data persistence."""

    def test_conversation_persistence(self, client, api_key_headers):
        """Test that conversation data persists across requests."""
        # Create conversation
        conv_id = client.post(
            "/api/v1/conversation/new",
            headers=api_key_headers,
        ).json()["conversation_id"]
        
        # Send message
        request = {
            "conversation_id": conv_id,
            "message": "Test message",
            "sender_id": "user",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "conversation_history": [],
        }
        
        client.post(
            "/api/v1/conversation/message",
            headers=api_key_headers,
            json=request,
        )
        
        # Retrieve conversation
        conv_data = client.get(
            f"/api/v1/conversation/{conv_id}",
            headers=api_key_headers,
        ).json()
        
        # Verify data persisted
        assert conv_data["conversation_id"] == conv_id
        assert len(conv_data["messages"]) == 2  # user + assistant
        assert conv_data["messages"][0]["role"] == "user"
        assert conv_data["messages"][1]["role"] == "assistant"
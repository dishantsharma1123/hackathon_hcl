"""Unit tests for agent service."""

import pytest
from app.agents.agent import AgentService
from app.agents.personas import PersonaType


class TestAgentService:
    """Tests for agent service."""

    @pytest.fixture
    def agent_service(self):
        """Create agent service instance."""
        return AgentService()

    def test_get_conversation_state_new(self, agent_service):
        """Test getting conversation state for new conversation."""
        state = agent_service.get_conversation_state("new-conv-123")
        
        assert "persona" in state
        assert "turn_count" in state
        assert "start_time" in state
        assert "last_activity" in state
        assert "extracted_intelligence" in state
        assert state["turn_count"] == 0
        assert state["persona"] is None

    def test_get_conversation_state_existing(self, agent_service):
        """Test getting existing conversation state."""
        conv_id = "existing-conv-456"
        agent_service.get_conversation_state(conv_id)
        
        # Get same conversation again
        state = agent_service.get_conversation_state(conv_id)
        assert state["turn_count"] == 0

    def test_get_engagement_metrics(self, agent_service):
        """Test getting engagement metrics."""
        conv_id = "metrics-conv-789"
        agent_service.get_conversation_state(conv_id)
        
        metrics = agent_service.get_engagement_metrics(conv_id)
        
        assert "conversation_turns" in metrics
        assert "engagement_duration_seconds" in metrics
        assert "last_activity" in metrics

    def test_should_continue_conversation_below_max(self, agent_service):
        """Test that conversation continues below max turns."""
        conv_id = "continue-conv-1"
        state = agent_service.get_conversation_state(conv_id)
        state["turn_count"] = 5
        
        assert agent_service.should_continue_conversation(conv_id) is True

    def test_should_continue_conversation_at_max(self, agent_service):
        """Test that conversation stops at max turns."""
        conv_id = "continue-conv-2"
        state = agent_service.get_conversation_state(conv_id)
        state["turn_count"] = 20
        
        assert agent_service.should_continue_conversation(conv_id) is False

    def test_should_continue_conversation_with_all_intel(self, agent_service):
        """Test that conversation stops with all intelligence extracted."""
        conv_id = "continue-conv-3"
        state = agent_service.get_conversation_state(conv_id)
        state["turn_count"] = 10
        state["extracted_intelligence"] = {
            "bank_accounts": ["1234567890"],
            "upi_ids": ["user@paytm"],
            "phishing_urls": ["http://scam.com"],
            "phone_numbers": ["9876543210"],
        }
        
        assert agent_service.should_continue_conversation(conv_id) is False

    def test_reset_conversation(self, agent_service):
        """Test resetting conversation state."""
        conv_id = "reset-conv-123"
        agent_service.get_conversation_state(conv_id)
        
        # Reset
        agent_service.reset_conversation(conv_id)
        
        # State should be gone
        assert conv_id not in agent_service.conversation_states

    def test_clean_response_quotes(self, agent_service):
        """Test cleaning response with quotes."""
        response = agent_service._clean_response('"This is a response"')
        assert response == "This is a response."

    def test_clean_response_prefix(self, agent_service):
        """Test cleaning response with prefix."""
        response = agent_service._clean_response("Response: This is a response")
        assert response == "This is a response."

    def test_clean_response_ending(self, agent_service):
        """Test cleaning response without proper ending."""
        response = agent_service._clean_response("This is a response")
        assert response.endswith(".")


class TestPersonaSelection:
    """Tests for persona selection logic."""

    def test_select_persona_lottery(self):
        """Test persona selection for lottery scam."""
        from app.agents.personas import select_persona
        
        message = "Congratulations! You've won Rs. 50,000 in our lottery!"
        persona = select_persona("lottery_prize", message)
        
        assert persona == PersonaType.LOTTERY_WINNER

    def test_select_persona_job(self):
        """Test persona selection for job scam."""
        from app.agents.personas import select_persona
        
        message = "Work from home! Earn Rs. 30,000/month."
        persona = select_persona("financial_fraud", message)
        
        assert persona == PersonaType.JOB_SEEKER

    def test_select_persona_business(self):
        """Test persona selection for business scam."""
        from app.agents.personas import select_persona
        
        message = "Buy in bulk and get 50% discount on all products!"
        persona = select_persona("financial_fraud", message)
        
        assert persona == PersonaType.BUSINESS_OWNER

    def test_select_persona_phishing(self):
        """Test persona selection for phishing scam."""
        from app.agents.personas import select_persona
        
        message = "Your bank account will be blocked. Verify now."
        persona = select_persona("phishing", message)
        
        assert persona == PersonaType.ELDERLY

    def test_select_persona_default(self):
        """Test default persona selection."""
        from app.agents.personas import select_persona
        
        message = "Some generic scam message"
        persona = select_persona("unknown", message)
        
        assert persona == PersonaType.ELDERLY  # Default persona

"""Agent service for managing autonomous conversations."""

import random
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.services.llm import llm_service
from app.agents.personas import PersonaType, select_persona, PERSONA_DEFINITIONS
from app.agents.prompts import get_persona_prompt, get_extraction_prompt
from app.utils.logger import app_logger
from app.config import settings


class AgentService:
    """Service for managing the autonomous honey-pot agent."""

    def __init__(self):
        self.conversation_states: Dict[str, Dict] = {}

    def get_conversation_state(self, conversation_id: str) -> Dict:
        """Get or create conversation state."""
        if conversation_id not in self.conversation_states:
            self.conversation_states[conversation_id] = {
                "persona": None,
                "turn_count": 0,
                "start_time": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "extracted_intelligence": {
                    "bank_accounts": [],
                    "upi_ids": [],
                    "phishing_urls": [],
                    "phone_numbers": [],
                },
            }
        return self.conversation_states[conversation_id]

    async def generate_response(
        self,
        message: str,
        conversation_id: str,
        scam_type: str,
        conversation_history: List[str] = None,
        extracted_intelligence: Dict = None,
    ) -> str:
        """
        Generate an agent response to engage the scammer.

        Args:
            message: The scammer's message
            conversation_id: Conversation identifier
            scam_type: Detected scam type
            conversation_history: Previous messages
            extracted_intelligence: Currently extracted intelligence

        Returns:
            Agent's response message
        """
        state = self.get_conversation_state(conversation_id)
        
        # Select persona if not already set
        if state["persona"] is None:
            state["persona"] = select_persona(scam_type, message)
            app_logger.info(f"Selected persona: {state['persona'].value} for conversation {conversation_id}")

        # Update state
        state["turn_count"] += 1
        state["last_activity"] = datetime.utcnow()
        
        if extracted_intelligence:
            state["extracted_intelligence"] = extracted_intelligence

        # Build conversation context
        context = self._build_context(conversation_history, message)

        # Get persona prompt
        persona = state["persona"]
        system_prompt = get_persona_prompt(persona)

        # Add extraction guidance if needed
        extraction_guidance = get_extraction_prompt(state["extracted_intelligence"])
        if extraction_guidance:
            system_prompt += extraction_guidance

        # Add turn-specific guidance
        system_prompt += self._get_turn_guidance(state["turn_count"], state["extracted_intelligence"])

        # Generate response
        response = await llm_service.generate(
            prompt=context,
            system_prompt=system_prompt,
            temperature=0.8,  # Slightly higher for more natural responses
            max_tokens=200,    # Keep responses concise
        )

        # Clean up response
        response = self._clean_response(response)

        app_logger.info(f"Agent response for conversation {conversation_id}: {response[:100]}...")

        return response

    def _build_context(self, conversation_history: List[str], current_message: str) -> str:
        """Build conversation context for the LLM."""
        context_parts = []
        
        if conversation_history:
            # Include last few messages for context
            recent_history = conversation_history[-6:]  # Last 6 messages
            for i, msg in enumerate(recent_history):
                role = "Scammer" if i % 2 == 0 else "You"
                context_parts.append(f"{role}: {msg}")
        
        context_parts.append(f"Scammer: {current_message}")
        context_parts.append("You:")
        
        return "\n\n".join(context_parts)

    def _get_turn_guidance(self, turn_count: int, extracted_intelligence: Dict) -> str:
        """Get turn-specific guidance for the agent."""
        guidance = "\n\nTURN-SPECIFIC GUIDANCE:\n"
        
        if turn_count == 1:
            guidance += "- This is the first turn. Start with a brief, natural response.\n"
            guidance += "- Show appropriate initial reaction based on the message.\n"
        elif turn_count == 2:
            guidance += "- Second turn. Ask a clarifying question to keep the conversation going.\n"
        elif turn_count == 3:
            guidance += "- Third turn. Express some interest or concern.\n"
            guidance += "- Try to extract more information naturally.\n"
        elif turn_count <= 5:
            guidance += "- Continue building rapport and trust.\n"
            guidance += "- Ask about payment methods, bank details, or websites.\n"
        elif turn_count <= 10:
            guidance += "- Maintain the conversation.\n"
            guidance += "- If you haven't gotten key information, ask more directly.\n"
        else:
            guidance += "- Keep the conversation engaging.\n"
            guidance += "- If you have the information, consider wrapping up naturally.\n"

        # Check if we have all intelligence
        has_all = all([
            extracted_intelligence.get("bank_accounts"),
            extracted_intelligence.get("upi_ids"),
            extracted_intelligence.get("phishing_urls"),
            extracted_intelligence.get("phone_numbers"),
        ])
        
        if has_all:
            guidance += "- You have extracted all key intelligence. You can start wrapping up the conversation.\n"

        return guidance

    def _clean_response(self, response: str) -> str:
        """Clean the agent's response."""
        # Remove common prefixes/suffixes
        response = response.strip()
        
        # Remove quotes if the entire response is quoted
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        elif response.startswith("'") and response.endswith("'"):
            response = response[1:-1]
        
        # Remove "Response:" or similar prefixes
        prefixes_to_remove = ["Response:", "You:", "AI:", "Assistant:"]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Ensure response ends naturally
        if not response.endswith((".", "!", "?", "...")):
            response += "."
        
        return response

    def get_engagement_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Get engagement metrics for a conversation."""
        state = self.get_conversation_state(conversation_id)
        
        duration = int((state["last_activity"] - state["start_time"]).total_seconds())
        
        return {
            "conversation_turns": state["turn_count"],
            "engagement_duration_seconds": duration,
            "last_activity": state["last_activity"],
        }

    def should_continue_conversation(self, conversation_id: str) -> bool:
        """Determine if conversation should continue."""
        state = self.get_conversation_state(conversation_id)
        
        # Stop if max turns reached
        if state["turn_count"] >= settings.max_conversation_turns:
            return False
        
        # Stop if we have all intelligence and enough turns
        has_all = all([
            state["extracted_intelligence"].get("bank_accounts"),
            state["extracted_intelligence"].get("upi_ids"),
            state["extracted_intelligence"].get("phishing_urls"),
            state["extracted_intelligence"].get("phone_numbers"),
        ])
        
        if has_all and state["turn_count"] >= 5:
            return False
        
        return True

    def reset_conversation(self, conversation_id: str) -> None:
        """Reset conversation state."""
        if conversation_id in self.conversation_states:
            del self.conversation_states[conversation_id]


# Global service instance
agent_service = AgentService()

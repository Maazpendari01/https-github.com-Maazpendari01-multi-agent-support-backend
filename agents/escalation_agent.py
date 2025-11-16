from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from utils.config import config
from utils.prompts import ESCALATION_SYSTEM_PROMPT
from utils.logger import logger
import json


class EscalationAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0,  # Deterministic for escalation decisions
        )
        self.escalation_threshold = 0.7
        logger.info("Escalation Agent initialized")

    def should_escalate(
        self, ticket_content: str, category: str, confidence: float
    ) -> dict:
        """
        Decide if ticket needs human intervention

        Args:
            ticket_content: Original ticket
            category: Ticket category
            confidence: Resolution confidence score

        Returns:
            dict with escalation decision and reason
        """
        try:
            logger.info(f"Evaluating escalation (confidence: {confidence})")

            # Auto-escalate rules
            if confidence < self.escalation_threshold:
                return {
                    "escalate": True,
                    "reason": f"Low confidence ({confidence:.2f} < {self.escalation_threshold})",
                }

            if category == "billing":
                return {
                    "escalate": True,
                    "reason": "Billing issues require human review",
                }

            # LLM decision for edge cases
            prompt = f"""TICKET: {ticket_content}
CATEGORY: {category}
CONFIDENCE: {confidence}

Should this be escalated to a human agent?

Consider:
- Does it require account access?
- Is customer explicitly asking for human?
- Is issue too complex for automation?

Output format (JSON):
{{
    "escalate": true/false,
    "reason": "brief explanation"
}}
"""

            messages = [
                SystemMessage(content=ESCALATION_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)
            result = json.loads(response.content)

            status = "ESCALATED" if result["escalate"] else "AUTO-RESOLVED"
            logger.info(f"Decision: {status} - {result['reason']}")

            return result

        except Exception as e:
            logger.error(f"Escalation agent error: {str(e)}")
            # Fail safe: escalate on error
            return {"escalate": True, "reason": f"Error in escalation logic: {str(e)}"}


# Test
if __name__ == "__main__":
    agent = EscalationAgent()

    # Test 1: High confidence
    result1 = agent.should_escalate("How do I reset my password?", "technical", 0.95)
    print("\nTest 1 (high confidence):", result1)

    # Test 2: Low confidence
    result2 = agent.should_escalate(
        "The system is behaving strangely", "technical", 0.4
    )
    print("\nTest 2 (low confidence):", result2)

    # Test 3: Billing
    result3 = agent.should_escalate("I was charged twice", "billing", 0.9)
    print("\nTest 3 (billing):", result3)

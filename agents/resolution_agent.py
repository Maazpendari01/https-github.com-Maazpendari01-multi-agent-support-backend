from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from utils.config import config
from utils.prompts import RESOLUTION_SYSTEM_PROMPT
from utils.logger import logger
import json


class ResolutionAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0.3,  # Slightly creative for natural responses
        )
        logger.info("Resolution Agent initialized")

    def generate_response(
        self, ticket_content: str, context: str, category: str, priority: str
    ) -> dict:
        """
        Generate customer-ready response using retrieved context

        Args:
            ticket_content: Original ticket
            context: Retrieved documentation
            category: Ticket category
            priority: Ticket priority

        Returns:
            dict with response and confidence score
        """
        try:
            logger.info("Generating resolution response")

            prompt = f"""CUSTOMER TICKET:
{ticket_content}

TICKET INFO:
- Category: {category}
- Priority: {priority}

RETRIEVED DOCUMENTATION:
{context}

Generate a helpful, professional response to the customer based on the documentation provided.
Also rate your confidence (0.0 to 1.0) in this response.

Output format (JSON):
{{
    "response": "your customer-ready response here",
    "confidence": 0.85
}}
"""

            messages = [
                SystemMessage(content=RESOLUTION_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = self.llm.invoke(messages)

            # Parse JSON response
            result = json.loads(response.content)

            logger.success(f"Resolution generated (confidence: {result['confidence']})")

            return {
                "response": result["response"],
                "confidence": result["confidence"],
                "raw_response": response.content,
            }

        except json.JSONDecodeError:
            logger.warning("Failed to parse resolution response, using fallback")
            return {
                "response": response.content,
                "confidence": 0.5,
                "raw_response": response.content,
                "error": "json_parse_failed",
            }
        except Exception as e:
            logger.error(f"Resolution agent error: {str(e)}")
            raise


# Test
if __name__ == "__main__":
    agent = ResolutionAgent()

    test_ticket = "I can't log in, didn't get password reset email"
    test_context = """To reset your password, click 'Forgot Password' on login page.
Check spam folder if email doesn't arrive within 5 minutes."""

    result = agent.generate_response(test_ticket, test_context, "technical", "high")

    print("\n" + "=" * 70)
    print("RESOLUTION:")
    print(result["response"])
    print(f"\nConfidence: {result['confidence']}")
    print("=" * 70)

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from utils.config import config
from utils.prompts import TRIAGE_SYSTEM_PROMPT
from utils.logger import logger
import json


class TriageAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=config.GROQ_API_KEY,
            model=config.GROQ_MODEL,
            temperature=0.1,  # Low temperature for consistent categorization
        )
        logger.info("Triage Agent initialized")

    def analyze_ticket(self, ticket_content: str) -> dict:
        """
        Analyze incoming ticket and extract category, priority, keywords

        Args:
            ticket_content: Raw ticket text from customer

        Returns:
            dict with category, priority, keywords
        """
        try:
            logger.info(f"Analyzing ticket: {ticket_content[:50]}...")

            messages = [
                SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
                HumanMessage(
                    content=f"Analyze this support ticket:\n\n{ticket_content}"
                ),
            ]

            response = self.llm.invoke(messages)

            # Parse JSON response
            result = json.loads(response.content)

            logger.success(
                f"Triage complete: {result['category']} - {result['priority']}"
            )

            return {
                "category": result["category"],
                "priority": result["priority"],
                "keywords": result["keywords"],
                "raw_response": response.content,
            }

        except json.JSONDecodeError:
            logger.error("Failed to parse triage response as JSON")
            # Fallback to safe defaults
            return {
                "category": "general",
                "priority": "medium",
                "keywords": ["support", "help"],
                "raw_response": response.content,
                "error": "json_parse_failed",
            }
        except Exception as e:
            logger.error(f"Triage agent error: {str(e)}")
            raise


# Test the agent
if __name__ == "__main__":
    agent = TriageAgent()

    test_ticket = "I can't log into my account. I've tried resetting my password but the email isn't arriving."

    result = agent.analyze_ticket(test_ticket)
    print("\n" + "=" * 50)
    print("TRIAGE RESULT:")
    print(json.dumps(result, indent=2))
    print("=" * 50)

from database.qdrant_manager import QdrantManager
from utils.logger import logger
from typing import List


class KnowledgeAgent:
    def __init__(self):
        self.vector_db = QdrantManager()
        logger.info("Knowledge Agent initialized")

    def retrieve_context(self, keywords: List[str], top_k: int = 3) -> List[dict]:
        """
        Retrieve relevant documentation based on keywords

        Args:
            keywords: List of search keywords from triage
            top_k: Number of results to return

        Returns:
            List of relevant documents
        """
        try:
            # Combine keywords into search query
            query = " ".join(keywords)

            logger.info(f"Retrieving context for: {query}")

            # Search vector database
            results = self.vector_db.search(query, top_k=top_k)

            logger.success(f"Retrieved {len(results)} relevant documents")

            return results

        except Exception as e:
            logger.error(f"Knowledge agent error: {str(e)}")
            raise


# Test the agent
if __name__ == "__main__":
    agent = KnowledgeAgent()

    test_keywords = ["login", "password", "email"]

    results = agent.retrieve_context(test_keywords)

    print("\n" + "=" * 70)
    print(f"KEYWORDS: {test_keywords}")
    print("=" * 70)
    for i, result in enumerate(results, 1):
        print(f"\nDocument {i} (relevance: {result['score']:.3f}):")
        print(f"{result['content']}")
    print("=" * 70)

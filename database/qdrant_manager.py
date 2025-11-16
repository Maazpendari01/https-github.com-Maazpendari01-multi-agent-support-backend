from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from utils.config import config
from utils.logger import logger
from typing import List
import uuid


class QdrantManager:
    def __init__(self):
        self.client = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
        )

        # Use sentence-transformers for embeddings (free, local)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dimensions
        self.collection_name = config.QDRANT_COLLECTION

        logger.info("Qdrant client initialized")

        # Create collection if doesn't exist
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")

                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # Dimension of all-MiniLM-L6-v2
                        distance=Distance.COSINE,
                    ),
                )
                logger.success(f"Collection created: {self.collection_name}")
            else:
                logger.info(f"Collection exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Error ensuring collection: {str(e)}")
            raise

    def add_documents(self, documents: List[dict]):
        """
        Add documents to vector database

        Args:
            documents: List of dicts with 'content' and optional 'metadata'
        """
        try:
            points = []

            for doc in documents:
                # Generate embedding
                vector = self.encoder.encode(doc["content"]).tolist()

                # Create point
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "content": doc["content"],
                        "metadata": doc.get("metadata", {}),
                    },
                )
                points.append(point)

            # Upsert to Qdrant
            self.client.upsert(collection_name=self.collection_name, points=points)

            logger.success(f"Added {len(points)} documents to Qdrant")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Search for similar documents

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of matching documents with scores
        """
        try:
            # Generate query embedding
            query_vector = self.encoder.encode(query).tolist()

            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )

            # Format results
            formatted_results = [
                {
                    "content": hit.payload["content"],
                    "metadata": hit.payload.get("metadata", {}),
                    "score": hit.score,
                }
                for hit in results
            ]

            logger.info(f"Found {len(formatted_results)} results for query")

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            raise


# Test the manager
if __name__ == "__main__":
    manager = QdrantManager()

    # Add sample documentation
    sample_docs = [
        {
            "content": "To reset your password, go to the login page and click 'Forgot Password'. You'll receive an email with reset instructions within 5 minutes.",
            "metadata": {"category": "authentication", "topic": "password_reset"},
        },
        {
            "content": "Our platform supports single sign-on (SSO) through Google, Microsoft, and GitHub. Contact your administrator to enable SSO for your organization.",
            "metadata": {"category": "authentication", "topic": "sso"},
        },
        {
            "content": "If you're not receiving password reset emails, check your spam folder. Also verify that noreply@example.com is not blocked.",
            "metadata": {"category": "authentication", "topic": "email_issues"},
        },
    ]

    print("\n📤 Adding documents to Qdrant...")
    manager.add_documents(sample_docs)

    print("\n🔍 Testing search...")
    query = "I didn't get the password reset email"
    results = manager.search(query, top_k=2)

    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (score: {result['score']:.3f}):")
        print(f"Content: {result['content']}")
        print(f"Metadata: {result['metadata']}")
    print("=" * 70)

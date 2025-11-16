from utils.logger import logger
from datetime import datetime
from typing import Dict, List, Optional


class AnalyticsAgent:
    def __init__(self):
        self.metrics: List[Dict] = []
        logger.info("Analytics Agent initialized")

    def track_ticket(self, state: Dict) -> Dict:
        """
        Extract and track metrics from ticket processing

        Args:
            state: Final state from workflow

        Returns:
            Metrics dictionary
        """
        try:
            metrics = {
                "ticket_id": state.get("ticket_id", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "category": state.get("category", "unknown"),
                "priority": state.get("priority", "unknown"),
                "response_time": state.get("response_time", 0.0),  # Default to 0.0
                "confidence": state.get("confidence", 0.0),  # Default to 0.0
                "escalated": state.get("escalate", False),
                "escalation_reason": state.get("escalation_reason", None),
            }

            self.metrics.append(metrics)

            logger.info(
                f"📊 Tracked metrics for ticket {state.get('ticket_id', 'unknown')}"
            )

            return metrics

        except Exception as e:
            logger.error(f"Analytics agent error: {str(e)}")
            return {}

    def get_summary(self) -> Dict:
        """Get summary statistics with null-safe calculations"""

        if not self.metrics:
            return {
                "message": "No metrics yet",
                "total_tickets": 0,
                "escalated_tickets": 0,
                "auto_resolved": 0,
                "escalation_rate": "0.0%",
                "avg_response_time": "0.00s",
                "avg_confidence": "0.00",
            }

        total = len(self.metrics)
        escalated = sum(1 for m in self.metrics if m.get("escalated", False))

        # Safe calculation for response time (filter out None/0 values)
        valid_response_times = [
            m["response_time"]
            for m in self.metrics
            if m.get("response_time") and m["response_time"] > 0
        ]
        avg_response_time = (
            sum(valid_response_times) / len(valid_response_times)
            if valid_response_times
            else 0.0
        )

        # Safe calculation for confidence (filter out None/0 values)
        valid_confidences = [
            m["confidence"]
            for m in self.metrics
            if m.get("confidence") and m["confidence"] > 0
        ]
        avg_confidence = (
            sum(valid_confidences) / len(valid_confidences)
            if valid_confidences
            else 0.0
        )

        return {
            "total_tickets": total,
            "escalated_tickets": escalated,
            "auto_resolved": total - escalated,
            "escalation_rate": f"{(escalated / total) * 100:.1f}%",
            "avg_response_time": f"{avg_response_time:.2f}s",
            "avg_confidence": f"{avg_confidence:.2f}",
        }

    def get_detailed_metrics(self) -> List[Dict]:
        """Get all tracked metrics"""
        return self.metrics

    def get_category_breakdown(self) -> Dict[str, int]:
        """Get ticket count by category"""
        breakdown = {}
        for m in self.metrics:
            category = m.get("category", "unknown")
            breakdown[category] = breakdown.get(category, 0) + 1
        return breakdown

    def get_priority_breakdown(self) -> Dict[str, int]:
        """Get ticket count by priority"""
        breakdown = {}
        for m in self.metrics:
            priority = m.get("priority", "unknown")
            breakdown[priority] = breakdown.get(priority, 0) + 1
        return breakdown

    def clear_metrics(self):
        """Clear all metrics (useful for testing)"""
        self.metrics = []
        logger.info("📊 Cleared all metrics")


# Test the agent
if __name__ == "__main__":
    agent = AnalyticsAgent()

    # Test with sample data
    test_states = [
        {
            "ticket_id": "TEST-001",
            "category": "technical",
            "priority": "high",
            "response_time": 2.5,
            "confidence": 0.85,
            "escalate": False,
            "escalation_reason": None,
        },
        {
            "ticket_id": "TEST-002",
            "category": "billing",
            "priority": "urgent",
            "response_time": 1.8,
            "confidence": 0.95,
            "escalate": True,
            "escalation_reason": "Billing issues require human review",
        },
        {
            "ticket_id": "TEST-003",
            "category": "general",
            "priority": "medium",
            "response_time": 3.2,
            "confidence": 0.75,
            "escalate": False,
            "escalation_reason": None,
        },
    ]

    # Track all test tickets
    for state in test_states:
        agent.track_ticket(state)

    # Print summary
    print("\n" + "=" * 70)
    print("ANALYTICS SUMMARY")
    print("=" * 70)
    summary = agent.get_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("CATEGORY BREAKDOWN")
    print("=" * 70)
    for category, count in agent.get_category_breakdown().items():
        print(f"{category}: {count}")

    print("\n" + "=" * 70)
    print("PRIORITY BREAKDOWN")
    print("=" * 70)
    for priority, count in agent.get_priority_breakdown().items():
        print(f"{priority}: {count}")
    print("=" * 70)

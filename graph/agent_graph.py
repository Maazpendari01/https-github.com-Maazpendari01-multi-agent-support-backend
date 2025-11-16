from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.triage_agent import TriageAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.resolution_agent import ResolutionAgent
from agents.escalation_agent import EscalationAgent
from agents.analytics_agent import AnalyticsAgent
from utils.logger import logger
import time


class MultiAgentWorkflow:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.resolution_agent = ResolutionAgent()
        self.escalation_agent = EscalationAgent()
        self.analytics_agent = AnalyticsAgent()

        self.graph = self._build_graph()
        logger.info("✅ Multi-agent workflow with all 5 agents initialized")

    def _build_graph(self):
        """Build complete 5-agent LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add all nodes
        workflow.add_node("triage", self.triage_node)
        workflow.add_node("knowledge", self.knowledge_node)
        workflow.add_node("resolution", self.resolution_node)
        workflow.add_node("escalation", self.escalation_node)
        workflow.add_node("analytics", self.analytics_node)

        # Define flow
        workflow.set_entry_point("triage")
        workflow.add_edge("triage", "knowledge")
        workflow.add_edge("knowledge", "resolution")
        workflow.add_edge("resolution", "escalation")
        workflow.add_edge("escalation", "analytics")
        workflow.add_edge("analytics", END)

        return workflow.compile()

    def triage_node(self, state: AgentState) -> AgentState:
        logger.info("🎯 Triage Agent")
        result = self.triage_agent.analyze_ticket(state["ticket_content"])
        return {
            **state,
            "category": result["category"],
            "priority": result["priority"],
            "keywords": result["keywords"],
        }

    def knowledge_node(self, state: AgentState) -> AgentState:
        logger.info("📚 Knowledge Agent")
        results = self.knowledge_agent.retrieve_context(state["keywords"])
        context = "\n\n".join(
            [
                f"[Doc {i + 1}, relevance: {r['score']:.2f}]\n{r['content']}"
                for i, r in enumerate(results)
            ]
        )
        return {**state, "retrieved_docs": results, "context": context}

    def resolution_node(self, state: AgentState) -> AgentState:
        logger.info("💡 Resolution Agent")
        result = self.resolution_agent.generate_response(
            state["ticket_content"],
            state["context"],
            state["category"],
            state["priority"],
        )
        return {
            **state,
            "response": result["response"],
            "confidence": result["confidence"],
        }

    def escalation_node(self, state: AgentState) -> AgentState:
        logger.info("⚠️  Escalation Agent")
        result = self.escalation_agent.should_escalate(
            state["ticket_content"], state["category"], state["confidence"]
        )
        return {
            **state,
            "escalate": result["escalate"],
            "escalation_reason": result["reason"],
        }

    def analytics_node(self, state: AgentState) -> AgentState:
        logger.info("📊 Analytics Agent")
        metrics = self.analytics_agent.track_ticket(state)
        return {**state, **metrics}

    def process_ticket(self, ticket_id: str, ticket_content: str) -> dict:
        start_time = time.time()

        logger.info(f"\n{'=' * 70}")
        logger.info(f"🎫 Processing Ticket: {ticket_id}")
        logger.info(f"{'=' * 70}\n")

        initial_state = {
            "ticket_id": ticket_id,
            "ticket_content": ticket_content,
            "category": None,
            "priority": None,
            "keywords": None,
            "retrieved_docs": None,
            "context": None,
            "response": None,
            "confidence": None,
            "escalate": None,
            "escalation_reason": None,
            "total_tokens": None,
            "response_time": None,
            "current_agent": None,
            "messages": [],
        }

        final_state = self.graph.invoke(initial_state)
        final_state["response_time"] = time.time() - start_time

        status = "🚨 ESCALATED" if final_state["escalate"] else "✅ AUTO-RESOLVED"
        logger.success(f"\n{status} in {final_state['response_time']:.2f}s\n")

        return final_state


# Test complete workflow
if __name__ == "__main__":
    workflow = MultiAgentWorkflow()

    test_tickets = [
        ("TICKET-001", "I can't log into my account"),
        ("TICKET-002", "I was charged twice this month"),
        ("TICKET-003", "How do I reset my password?"),
    ]

    for ticket_id, content in test_tickets:
        result = workflow.process_ticket(ticket_id, content)

        print(f"\n{'=' * 70}")
        print(f"TICKET: {ticket_id}")
        print(f"Category: {result['category']} | Priority: {result['priority']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Escalated: {result['escalate']} ({result['escalation_reason']})")
        print(f"\nRESPONSE:\n{result['response']}")
        print(f"{'=' * 70}\n")

    # Summary
    print("\n📊 ANALYTICS SUMMARY:")
    print(workflow.analytics_agent.get_summary())

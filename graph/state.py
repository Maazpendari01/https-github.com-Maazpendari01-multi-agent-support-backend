from typing import TypedDict, List, Optional
from pydantic import BaseModel


class AgentState(TypedDict):
    """Shared state passed between agents"""

    # Input
    ticket_id: str
    ticket_content: str

    # Triage output
    category: Optional[str]
    priority: Optional[str]
    keywords: Optional[List[str]]

    # Knowledge output
    retrieved_docs: Optional[List[dict]]
    context: Optional[str]

    # Resolution output
    response: Optional[str]
    confidence: Optional[float]

    # Escalation output
    escalate: Optional[bool]
    escalation_reason: Optional[str]

    # Analytics
    total_tokens: Optional[int]
    response_time: Optional[float]

    # Status
    current_agent: Optional[str]
    messages: Optional[List[str]]

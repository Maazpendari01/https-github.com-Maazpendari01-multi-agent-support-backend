from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from graph.agent_graph import MultiAgentWorkflow
from database.supabase_client import SupabaseManager
from utils.logger import logger
import uuid

router = APIRouter()

# Initialize workflow and database
workflow = MultiAgentWorkflow()
db = SupabaseManager()


# Request/Response models
class TicketSubmit(BaseModel):
    content: str


class TicketResponse(BaseModel):
    ticket_id: str
    category: str
    priority: str
    response: str
    confidence: float
    escalated: bool
    escalation_reason: str | None
    response_time: float


@router.post("/tickets", response_model=TicketResponse)
async def submit_ticket(ticket: TicketSubmit):
    """Submit a new support ticket"""
    try:
        # Generate ticket ID
        ticket_id = f"TICKET-{str(uuid.uuid4())[:8].upper()}"

        logger.info(f"API: Received ticket {ticket_id}")

        # Process through workflow
        result = workflow.process_ticket(ticket_id, ticket.content)

        # Save to database
        db.save_ticket(result)

        return TicketResponse(
            ticket_id=result["ticket_id"],
            category=result["category"],
            priority=result["priority"],
            response=result["response"],
            confidence=result["confidence"],
            escalated=result["escalate"],
            escalation_reason=result["escalation_reason"],
            response_time=result["response_time"],
        )

    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get ticket by ID"""
    try:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
async def list_tickets(limit: int = 100):
    """List all tickets"""
    try:
        tickets = db.get_all_tickets(limit)
        return {"tickets": tickets, "count": len(tickets)}
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics():
    """Get analytics summary"""
    try:
        summary = workflow.analytics_agent.get_summary()
        return summary
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

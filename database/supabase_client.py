from supabase import create_client, Client
from utils.config import config
from utils.logger import logger
from datetime import datetime
from typing import Dict, List


class SupabaseManager:
    def __init__(self):
        self.client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("Supabase client initialized")
        self._ensure_tables()

    def _ensure_tables(self):
        """Create tables if they don't exist"""
        # Note: Run this SQL in Supabase SQL Editor once:
        """
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            category TEXT,
            priority TEXT,
            response TEXT,
            confidence FLOAT,
            escalated BOOLEAN,
            escalation_reason TEXT,
            response_time FLOAT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category);
        CREATE INDEX IF NOT EXISTS idx_tickets_escalated ON tickets(escalated);
        """
        logger.info("Ensure tables exist in Supabase")

    def save_ticket(self, ticket_data: Dict) -> Dict:
        """Save ticket to database"""
        try:
            data = {
                "id": ticket_data["ticket_id"],
                "content": ticket_data["ticket_content"],
                "category": ticket_data.get("category"),
                "priority": ticket_data.get("priority"),
                "response": ticket_data.get("response"),
                "confidence": ticket_data.get("confidence"),
                "escalated": ticket_data.get("escalate", False),
                "escalation_reason": ticket_data.get("escalation_reason"),
                "response_time": ticket_data.get("response_time"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            result = self.client.table("tickets").insert(data).execute()

            logger.success(f"Saved ticket {ticket_data['ticket_id']} to database")
            return result.data[0] if result.data else {}

        except Exception as e:
            logger.error(f"Error saving ticket: {str(e)}")
            raise

    def get_ticket(self, ticket_id: str) -> Dict:
        """Get ticket by ID"""
        try:
            result = (
                self.client.table("tickets").select("*").eq("id", ticket_id).execute()
            )
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"Error getting ticket: {str(e)}")
            raise

    def get_all_tickets(self, limit: int = 100) -> List[Dict]:
        """Get all tickets"""
        try:
            result = (
                self.client.table("tickets")
                .select("*")
                .limit(limit)
                .order("created_at", desc=True)
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Error getting tickets: {str(e)}")
            raise

"""APEX Database Models"""
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from dataclasses import dataclass, field
from typing import List

Base = declarative_base()


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(String, primary_key=True)
    type = Column(String)
    source = Column(String)
    score = Column(Float, default=0)
    risk = Column(String)
    estimated_value = Column(Float, default=0)
    action = Column(String)
    status = Column(String, default="discovered")
    cycle_id = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"
    id = Column(String, primary_key=True)
    opportunity_id = Column(String)
    score = Column(Float)
    risk = Column(String)
    estimated_value = Column(Float)
    action_taken = Column(String)
    status = Column(String, default="new")
    cycle_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class RevenueRecord(Base):
    __tablename__ = "revenue_records"
    id = Column(String, primary_key=True)
    cycle_id = Column(String)
    lead_id = Column(String)
    amount = Column(Float)
    stripe_invoice_id = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True)
    key_hash = Column(String, unique=True)
    tenant_id = Column(String)
    tier = Column(String, default="starter")
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    usage_limit = Column(Integer, default=10000)
    created_at = Column(DateTime, default=datetime.utcnow)


class AgentStatus:
    pass


@dataclass
class SystemMetrics:
    total_revenue: float = 0.0
    cycles_completed: int = 0
    total_leads: int = 0
    deals_closed: int = 0
    active_subscriptions: int = 0
    cycle_history: List[dict] = field(default_factory=list)

    def record_cycle(self, cycle_id: str, opportunities: int, qualified: int, actions: int, revenue: float):
        self.cycles_completed += 1
        self.total_leads += opportunities
        self.deals_closed += actions
        self.total_revenue += revenue
        self.cycle_history.append({
            "cycle_id": cycle_id,
            "opportunities": opportunities,
            "qualified": qualified,
            "actions": actions,
            "revenue": revenue,
        })

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(20), unique=True, index=True, nullable=False)
    employee_id = Column(String(50), nullable=False, default="EMP001")
    category = Column(String(100), nullable=False)
    priority = Column(String(50), nullable=False, default="Medium")
    status = Column(String(50), nullable=False, default="Open")
    description = Column(Text, nullable=False)
    diagnostics = Column(Text, nullable=True)
    session_id = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

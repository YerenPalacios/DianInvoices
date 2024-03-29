from typing import List

from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from db import Base


dian_event_id = Table(
    "dian_invoice_events",
    Base.metadata,
    Column("invoice_id", ForeignKey("DianInvoice.id")),
    Column("event_id", ForeignKey("DianEvent.id")),
)


class DianEvent(Base):
    __tablename__ = 'DianEvent'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    code = Column(String(length=10))
    description = Column(String(length=100))
    date = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<DianEvent(id={self.id})>"

class DianInvoice(Base):
    __tablename__ = 'DianInvoice'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    cufe = Column(String(length=100))
    graphic_link = Column(String(length=300))
    total = Column(Integer)
    iva = Column(Integer)
    serie = Column(String(length=10))
    folio = Column(String(length=10))
    issue_date = Column(DateTime(timezone=True))
    seller_id = Column(Integer, ForeignKey("DianEntity.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("DianEntity.id"), nullable=False)

    seller = relationship("DianEntity",foreign_keys=[seller_id], back_populates="sent_invoices")
    receiver = relationship("DianEntity", foreign_keys=[receiver_id], back_populates="received_invoices")
    events: Mapped[List[DianEvent]] = relationship(secondary=dian_event_id)

    def __repr__(self):
        return f"<DianInvoice(id={self.id})>"

class DianEntity(Base):
    __tablename__ = "DianEntity"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    nit = Column(String(length=10))
    name = Column(String(length=50))
    received_invoices = relationship("DianInvoice", foreign_keys=[DianInvoice.receiver_id], back_populates="receiver")
    sent_invoices = relationship("DianInvoice", foreign_keys=[DianInvoice.seller_id], back_populates="seller")

    def __repr__(self):
        return f"<DianEntity(id={self.id})>"

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from schemas import InvoicePayload
from services.dian_invoice_service import DianInvoiceService


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/v1/get_invoice_information")
async def get_invoice_information(request: InvoicePayload, db: Session = Depends(get_db)):
    service = DianInvoiceService(db)
    dian_invoices = service.get_dian_invoices(request.cufes)
    return dian_invoices

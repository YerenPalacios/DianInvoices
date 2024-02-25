from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from db import Base, engine, SessionLocal
from schemas import InvoicePayloadSh, DianInvoiceSh
from services.dian_invoice_service import DianInvoiceService


Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
app.add_middleware(
    DebugToolbarMiddleware,
    panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/v1/get_invoice_information")
async def get_invoice_information(request: InvoicePayloadSh, db: Session = Depends(get_db)) -> dict[str, DianInvoiceSh]:
    """ With the given cufes, this endpoint will get the invoice information from Dian url
        if the data is not saved in the database else it will return database information """
    service = DianInvoiceService(db)
    dian_invoices = service.get_dian_invoices(request.cufes)
    return dian_invoices

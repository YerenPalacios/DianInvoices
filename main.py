from fastapi import FastAPI

from models import InvoicePayload
from services.dian_invoice_service import DianInvoiceService

app = FastAPI()


@app.post("/api/v1/get_invoice_information")
async def get_invoice_information(request: InvoicePayload):
    service = DianInvoiceService()
    dian_invoices = service.get_dian_invoices(request.cufes)
    return dian_invoices

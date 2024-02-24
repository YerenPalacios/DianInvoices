from typing import Dict

from repositories import DianInvoiceRepository
from schemas import DianInvoiceSh
from scrappers.dian_scrapper import DianScrapper


class DianInvoiceService:

    def __init__(self, db):
        self.dian_invoice_repository = DianInvoiceRepository(db)
        self.scrapper = DianScrapper()

    def get_dian_invoices(self, invoice_cufes: list[str]) -> Dict[str, DianInvoiceSh]:
        db_dian_invoices = self.dian_invoice_repository.get_dian_invoices(invoice_cufes)
        not_in_db_cufes = [invoice_id for invoice_id in invoice_cufes if invoice_id not in db_dian_invoices.keys()]
        web_dian_invoices = self.scrapper.get_dian_invoices(not_in_db_cufes)
        self.dian_invoice_repository.save_invoices(web_dian_invoices)
        return {**db_dian_invoices, **self.scrapper.get_web_information_as_schemas(web_dian_invoices)}

from typing import Dict

from repositories import DianInvoiceRepository
from schemas import DianInvoice, DianEvent, DianEntityInformation
from scrappers.dian_scrapper import DianScrapper


class DianInvoiceService:

    def __init__(self, db):
        self.dian_invoice_repository = DianInvoiceRepository(db)

    @staticmethod
    def get_dian_web_invoices(invoice_ids: list[str]) -> Dict[str, DianInvoice]:
        scrapper = DianScrapper()
        scrapper_invoices = scrapper.get_dian_invoices(invoice_ids)
        dian_invoices = {}
        for scrapper_invoice in scrapper_invoices:
            seller_information = DianEntityInformation(
                document=scrapper_invoice.get("seller_information", {}).get("NIT"),
                name=scrapper_invoice.get("seller_information", {}).get("Nombre")
            )

            receiver_information = DianEntityInformation(
                document=scrapper_invoice.get("receiver_information", {}).get("NIT"),
                name=scrapper_invoice.get("receiver_information", {}).get("Nombre")
            )

            events = [
                DianEvent(
                    eventNumber=event.get("code", ""),
                    eventName=event.get("description", "")
                ) for event in scrapper_invoice["events"]
            ]

            dian_invoices[scrapper_invoice.pop("cufe")] = DianInvoice(
                events=events,
                seller_information=seller_information,
                receiver_information=receiver_information,
                link_graphic_representation=scrapper_invoice["link_graphic_representation"]
            )
        return dian_invoices

    def get_db_dian_invoices(self):
        return self.dian_invoice_repository.get_dian_invoices()

    def get_dian_invoices(self, invoice_ids: list[str]) -> Dict[str, DianInvoice]:
        # self.get_db_dian_invoices()
        web_dian_invoices = self.get_dian_web_invoices(invoice_ids)
        return web_dian_invoices

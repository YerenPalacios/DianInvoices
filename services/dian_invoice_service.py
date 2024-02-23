from typing import Dict

from models import DianInvoice, DianEvent, DianEntityInformation
from scrappers.dian_scrapper import DianScrapper


class DianInvoiceService:

    @staticmethod
    def get_dian_invoices(invoice_ids: list[str]) -> Dict[str, DianInvoice]:
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

            dian_invoices[scrapper_invoice.pop("cufe")] = DianInvoice(
                events=[DianEvent(eventNumber=2, eventName="")],
                seller_information=seller_information,
                receiver_information=receiver_information,
                link_graphic_representation=scrapper_invoice["link_graphic_representation"]
            )
        return dian_invoices


from datetime import datetime
from typing import List, Dict

from sqlalchemy.orm import Session, joinedload

from models import DianInvoice, DianEntity, DianEvent
from schemas import DianInvoiceSh, DianEventSh, DianEntitySh


class DianInvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_dian_invoices(self, invoice_cufes) -> Dict[str, DianInvoiceSh]:
        db_dian_invoices = self.db.query(DianInvoice).options(
            joinedload(DianInvoice.seller),
            joinedload(DianInvoice.receiver),
            joinedload(DianInvoice.events)
        ).filter(
            DianInvoice.cufe.in_(invoice_cufes)
        ).all()
        dian_invoices = {}
        for db_dian_invoice in db_dian_invoices:
            dian_events = [DianEventSh(
                eventNumber=db_dian_event.code,
                eventName=db_dian_event.description
            ) for db_dian_event in db_dian_invoice.events]

            seller = DianEntitySh(
                document=db_dian_invoice.seller.nit,
                name=db_dian_invoice.seller.name
            )
            receiver = DianEntitySh(
                document=db_dian_invoice.receiver.nit,
                name=db_dian_invoice.receiver.name
            )
            dian_invoices[db_dian_invoice.cufe] = DianInvoiceSh(
                events=dian_events,
                seller_information=seller,
                receiver_information=receiver,
                link_graphic_representation=db_dian_invoice.graphic_link
            )
        return dian_invoices

    def get_or_create_dian_entity(self, name: str, nit: str) -> DianEntity:
        db_entity = self.db.query(DianEntity).filter(DianEntity.nit == nit).first()
        if db_entity:
            return db_entity
        db_entity = DianEntity(name=name, nit=nit)
        self.db.add(db_entity)
        self.db.commit()
        return db_entity

    def get_or_add_dian_invoice(self, data: dict, seller_id: int, receiver_id: int) -> DianInvoice:
        db_invoice = self.db.query(DianInvoice).filter(DianInvoice.cufe == data["CUFE"]).first()
        if db_invoice:
            return db_invoice
        db_invoice = DianInvoice(
            cufe=data["CUFE"],
            graphic_link=data["link_graphic_representation"],
            total=float(data["Total"].replace("$", "").replace(",", "")),
            iva=float(data["IVA"].replace("$", "").replace(",", "")),
            serie=data["Serie"],
            folio=data["Folio"],
            issue_date=datetime.strptime(data["Fecha de emisión de la factura Electrónica"], "%d-%m-%Y"),
            seller_id=seller_id,
            receiver_id=receiver_id,
        )
        self.db.add(db_invoice)
        return db_invoice

    def get_or_add_dian_events(self, data) -> DianEvent:
        db_event = self.db.query(DianEvent).filter(
            DianEvent.code == data["code"],
            DianEvent.description == data["description"]
        ).first()

        if db_event:
            return db_event

        db_event = DianEvent(
            code=data["code"],
            description=data["description"]
        )
        self.db.add(db_event)
        self.db.commit()
        return db_event


    def save_invoices(self, web_dian_invoices: List[Dict[str, str | dict]]):
        for web_dian_invoice in web_dian_invoices:
            web_invoice_seller = web_dian_invoice.get("seller_information")
            web_invoice_receiver = web_dian_invoice.get("receiver_information")
            seller = self.get_or_create_dian_entity(
                name=web_invoice_seller["Nombre"],
                nit=web_invoice_seller["NIT"]
            )
            receiver = self.get_or_create_dian_entity(
                name=web_invoice_receiver["Nombre"],
                nit=web_invoice_receiver["NIT"]
            )
            dian_invoice = self.get_or_add_dian_invoice(web_dian_invoice, seller.id, receiver.id)

            for event in web_dian_invoice["events"]:
                db_event = self.get_or_add_dian_events(event)
                dian_invoice.events.append(db_event)

        self.db.commit()

from pydantic import BaseModel


class InvoicePayloadSh(BaseModel):
    cufes: list[str]


class DianEventSh(BaseModel):
    eventNumber: str
    eventName: str


class DianEntitySh(BaseModel):
    document: str
    name: str


class DianInvoiceSh(BaseModel):
    events: list[DianEventSh]
    seller_information: DianEntitySh
    receiver_information: DianEntitySh
    link_graphic_representation: str

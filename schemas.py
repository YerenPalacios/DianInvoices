from pydantic import BaseModel


class InvoicePayload(BaseModel):
    cufes: list[str]


class DianEvent(BaseModel):
    eventNumber: str
    eventName: str


class DianEntityInformation(BaseModel):
    document: str
    name: str


class DianInvoice(BaseModel):
    events: list[DianEvent]
    seller_information: DianEntityInformation
    receiver_information: DianEntityInformation
    link_graphic_representation: str

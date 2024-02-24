from models import DianInvoice


class DianInvoiceRepository:
    def __init__(self, db):
        self.db = db

    def get_dian_invoices(self):
        return self.db.query(DianInvoice).all()

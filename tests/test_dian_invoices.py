import pytest
from datetime import datetime

from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from starlette.testclient import TestClient

from db import Base
from main import app, get_db
from models import DianInvoice, DianEntity, DianEvent

# TODO: test with mysql
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    yield db
    db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup():
    Base.metadata.create_all(bind=engine)


def test_get_dian_invoices(test_db: Session):
    test_cufe = "2320c5d9dcb19b24b9e8baa0e033579a1b1329bb1c846850838c8b6daedb90d36f528a727a79041869b68b7c2f2352c0"
    payload = {
        "cufes": [
            test_cufe
        ]
    }
    res = client.post("/api/v1/get_invoice_information", json=payload)
    data = res.json()
    db_query = test_db.query(DianInvoice).all()
    print(res.json())
    assert res.status_code == 200
    assert len(db_query) == 1
    assert db_query[0].cufe == test_cufe
    assert db_query[0].graphic_link == "https://catalogo-vpfe.dian.gov.co/Document/DownloadPDF?trackId=2320c5d9dcb19b24b9e8baa0e033579a1b1329bb1c846850838c8b6daedb90d36f528a727a79041869b68b7c2f2352c0&token=a79521cb02c123b723f0e8903e10543afb320d0b5125de1e3952b6eb5e21d98c"
    assert db_query[0].total == 237729
    assert db_query[0].iva == 37957
    assert db_query[0].folio == "428"
    assert db_query[0].issue_date == datetime.strptime("05-01-2024", "%d-%m-%Y")
    assert db_query[0].seller.nit == "901596817"
    assert db_query[0].seller.name == "COLOMBIA PLATAFORM SAS"
    assert db_query[0].receiver.nit == "800071617"
    assert db_query[0].receiver.name == "CUMMINS DE LOS ANDES S.A"
    assert db_query[0].events[0].code == "030"
    assert db_query[0].events[0].description == "Acuse de recibo de la Factura Electrónica de Venta"
    assert db_query[0].events[1].code == "032"
    assert db_query[0].events[1].description == "Recibo del bien o prestación del servicio"

    assert data[test_cufe]["seller_information"] == {'document': '901596817', 'name': 'COLOMBIA PLATAFORM SAS'}
    assert data[test_cufe]["receiver_information"] == {'document': '800071617', 'name': 'CUMMINS DE LOS ANDES S.A'}
    assert data[test_cufe]["link_graphic_representation"] == "https://catalogo-vpfe.dian.gov.co/Document/DownloadPDF?trackId=2320c5d9dcb19b24b9e8baa0e033579a1b1329bb1c846850838c8b6daedb90d36f528a727a79041869b68b7c2f2352c0&token=a79521cb02c123b723f0e8903e10543afb320d0b5125de1e3952b6eb5e21d98c"
    assert data[test_cufe]["events"][0] == {'eventNumber': '030', 'eventName': 'Acuse de recibo de la Factura Electrónica de Venta'}
    assert data[test_cufe]["events"][1] == {'eventNumber': '032', 'eventName': 'Recibo del bien o prestación del servicio'}
    test_db.delete(db_query[0])
    test_db.commit()


def test_get_dian_invoices_not_found(test_db: Session):
    test_cufe = "invalidcufe1234"
    payload = {
        "cufes": [
            test_cufe
        ]
    }
    res = client.post("/api/v1/get_invoice_information", json=payload)
    data = res.json()
    db_query = test_db.query(DianInvoice).all()
    assert res.status_code == 200
    assert len(db_query) == 0
    assert data == {}


def test_get_dian_invoices_from_db(test_db: Session):
    test_cufe = "2320c5d9dcb1"
    event = DianEvent(code="01", description="test event", date=datetime.now())
    test_db_dian_entity = DianEntity(nit="1", name="1E")
    test_db_dian_entity2 = DianEntity(nit="2", name="1X")
    test_db_invoice = DianInvoice(
        cufe=test_cufe,
        graphic_link="http://example.com",
        total=100,
        iva=1,
        serie="S",
        folio="SE",
        issue_date=datetime.now(),
        seller=test_db_dian_entity,
        receiver=test_db_dian_entity2,
        events=[event]
    )
    test_db.add(test_db_invoice)
    test_db.commit()
    payload = {
        "cufes": [
            test_cufe
        ]
    }
    res = client.post("/api/v1/get_invoice_information", json=payload)
    data = res.json()

    assert res.status_code == 200
    assert len(data.keys()) == 1
    assert list(data.keys())[0] == test_cufe
    assert data[test_cufe]["seller_information"] == {'document': '1', 'name': '1E'}
    assert data[test_cufe]["receiver_information"] == {'document': '2', 'name': '1X'}
    assert data[test_cufe]["link_graphic_representation"] == "http://example.com"
    assert data[test_cufe]["events"] == [{'eventNumber': '01', 'eventName': 'test event'}]


def teardown():
    Base.metadata.drop_all(bind=engine)

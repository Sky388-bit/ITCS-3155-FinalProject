from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from ..controllers import customers as controller
from ..main import app
import pytest
from ..models import customers as model
from ..schemas import customers as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_customer(db_session):
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "address": "123 Main St"
    }
    customer_object = schema.CustomersCreate(**customer_data)
    created_customer = controller.create(db_session, customer_object)

    assert created_customer is not None
    assert created_customer.first_name == "John"
    assert created_customer.last_name == "Doe"
    assert db_session.add.called
    assert db_session.commit.called
    assert db_session.refresh.called


def test_read_all_customers(db_session):
    mock_customers = [
        model.Customers(id=1, first_name="John", last_name="Doe"),
        model.Customers(id=2, first_name="Jane", last_name="Doe")
    ]
    db_session.query.return_value.all.return_value = mock_customers

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"


def test_read_one_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe")
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"


def test_update_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe")
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_customer

    update_data = schema.CustomersUpdate(first_name="Johnny")
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert mock_query.update.called
    assert db_session.commit.called


def test_delete_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe")
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_customer

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert mock_query.delete.called
    assert db_session.commit.called

def test_read_one_customer_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.read_one(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"

def test_update_customer_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = schema.CustomersUpdate(first_name="John")

    with pytest.raises(HTTPException) as exc_info:
        controller.update(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"

def test_delete_customer_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"
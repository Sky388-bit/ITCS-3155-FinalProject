from fastapi import HTTPException
from fastapi.testclient import TestClient
from ..controllers import orders as order_controller
from ..controllers import payment_info as payment_controller
from ..main import app
import pytest
from ..models import orders as order_model
from ..models import payment_info as payment_model

# Tests interaction between orders.py and payment_info.py
# Create a test client for the app
client = TestClient(app)

@pytest.fixture
def db_session(mocker):
    return mocker.Mock()

def test_create_guest_order(db_session):
    # Sample data for a guest checkout
    order_data = {
        "customers_name": "Guest User",
        "customers_email": "guest@example.com",
        "customers_phone": "123-456-7890",
        "order_type": "Takeout",
        "order_status": "Cart",
    }


    order_object = order_model.Order(**order_data)


    created_order = order_controller.create(db_session, order_object)


    assert created_order is not None
    assert created_order.customers_name == "Guest User"
    assert created_order.customers_email == "guest@example.com"
    assert created_order.customers_phone == "123-456-7890"
    assert created_order.order_type == "Takeout"
    assert created_order.order_status == "Cart"

def test_full_checkout_flow(db_session):
    # Mock order creation
    order_data = {
        "customers_name": "Integration Test",
        "customers_email": "test@example.com",
        "customers_phone": "000-000-0000",
        "order_type": "Takeout",
        "order_status": "Placed",
        "total_price": 50.00
    }
    order_object = order_model.Order(**order_data)
    
    # Set up the query mock to return the order_object when .first() is called
    # and an empty list when .all() is called.
    query_mock = db_session.query.return_value.filter.return_value
    query_mock.first.return_value = order_object
    query_mock.all.return_value = [] # Past Payments empty

    # Sample payment data
    payment_data = {
        "transaction_status": "Success",
        "payment_type": "Credit Card",
        "amount": 50.00,
        "order_id": 1
    }

    payment_object = payment_model.PaymentInfo(**payment_data)

    created_payment = payment_controller.create(db_session, payment_object)

    assert created_payment is not None
    assert created_payment.amount == 50.00
    assert created_payment.transaction_status == "Success"
    assert order_object.order_status == "Paid"

def test_create_guest_order_missing_info(db_session):
    order_data = {
        "customers_name": "Guest",
        "order_type": "Takeout",
    }
    order_object = order_model.Order(**order_data)

    with pytest.raises(HTTPException) as exc_info:
        order_controller.create(db_session, order_object)
    assert exc_info.value.status_code == 400

def test_create_delivery_no_address(db_session):
    order_data = {
        "customers_name": "Guest",
        "customers_email": "a@b.com",
        "customers_phone": "123-456-7890",
        "order_type": "Delivery",
        "description": None
    }
    order_object = order_model.Order(**order_data)

    with pytest.raises(HTTPException) as exc_info:
        order_controller.create(db_session, order_object)
    assert exc_info.value.status_code == 400

def test_create_payment_order_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    payment_data = {
        "order_id": 999,
        "amount": 10.00,
        "transaction_status": "Success",
    }
    payment_object = payment_model.PaymentInfo(**payment_data)

    with pytest.raises(HTTPException) as exc_info:
        payment_controller.create(db_session, payment_object)
    assert exc_info.value.status_code == 404
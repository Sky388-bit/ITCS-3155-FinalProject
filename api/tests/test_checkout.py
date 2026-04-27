from fastapi.testclient import TestClient
from ..controllers import orders as order_controller
from ..controllers import payment_info as payment_controller
from ..main import app
import pytest
from ..models import orders as order_model
from ..models import payment_info as payment_model

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
        "tracking_number": "TRK-001"
    }


    order_object = order_model.Order(**order_data)


    created_order = order_controller.create(db_session, order_object)


    assert created_order is not None
    assert created_order.customers_email == "guest@example.com"
    assert created_order.order_type == "Takeout"

def test_create_payment(db_session):
    # Sample payment data
    payment_data = {
        "transaction_status": "Success",
        "payment_type": "Credit Card",
        "amount": 10.00,
        "order_id": 1
    }

    payment_object = payment_model.PaymentInfo(**payment_data)


    created_payment = payment_controller.create(db_session, payment_object)

    assert created_payment is not None
    assert created_payment.amount == 10.00
    assert created_payment.transaction_status == "Success"

from fastapi.testclient import TestClient
from fastapi import HTTPException
from ..controllers import payment_info as controller
from ..main import app
import pytest
from ..models import payment_info as model, orders as orders_model
from ..schemas import payment_info as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_payment_info(db_session, mocker):
    payment_data = {
        "transaction_status": "Success",
        "payment_type": "Credit Card",
        "amount": 100.0,
        "order_id": 1
    }
    payment_object = schema.PaymentInfoCreate(**payment_data)

    mock_order = orders_model.Order(id=1, total_price=100.0, order_status="Placed")

    def query_side_effect(model_class):
        mock_query = mocker.Mock()
        if model_class == orders_model.Order:
            mock_query.filter.return_value.first.return_value = mock_order
        elif model_class == model.PaymentInfo:
            mock_query.filter.return_value.all.return_value = []
        return mock_query

    db_session.query.side_effect = query_side_effect

    created_payment = controller.create(db_session, payment_object)

    assert created_payment is not None
    assert created_payment.amount == 100.0
    assert mock_order.order_status == "Paid"
    assert db_session.add.called
    assert db_session.commit.called


def test_read_all_payment_info(db_session):
    mock_payments = [
        model.PaymentInfo(id=1, amount=100.0, order_id=1),
        model.PaymentInfo(id=2, amount=50.0, order_id=2)
    ]
    db_session.query.return_value.all.return_value = mock_payments

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2


def test_read_one_payment_info(db_session):
    mock_payment = model.PaymentInfo(id=1, amount=100.0, order_id=1)
    db_session.query.return_value.filter.return_value.first.return_value = mock_payment

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.amount == 100.0


def test_update_payment_info(db_session):
    mock_payment = model.PaymentInfo(id=1, amount=100.0, order_id=1)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_payment

    update_data = schema.PaymentInfoUpdate(transaction_status="Failed")
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert mock_query.update.called
    assert db_session.commit.called


def test_delete_payment_info(db_session):
    mock_payment = model.PaymentInfo(id=1, amount=100.0, order_id=1)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_payment

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert mock_query.delete.called
    assert db_session.commit.called


def test_create_payment_info_order_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    payment_data = schema.PaymentInfoCreate(
        transaction_status="Success",
        payment_type="Credit Card",
        amount=100.0,
        order_id=999
    )

    with pytest.raises(HTTPException) as exc_info:
        controller.create(db_session, payment_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Order not found"


def test_update_payment_info_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = schema.PaymentInfoUpdate(transaction_status="Failed")
    with pytest.raises(HTTPException) as exc_info:
        controller.update(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"


def test_delete_payment_info_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"

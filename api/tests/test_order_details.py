from fastapi.testclient import TestClient
from fastapi import HTTPException
from ..controllers import order_details as controller
from ..main import app
import pytest
from ..models import order_details as model, menu as menu_model, orders as orders_model
from ..schemas import order_details as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order_detail(db_session, mocker):
    order_detail_data = {
        "order_id": 1,
        "menu_id": 1,
        "amount": 2
    }
    order_detail_object = schema.OrderDetailCreate(**order_detail_data)

    mock_menu_item = menu_model.Menu(id=1, price=10.0)
    mock_order = orders_model.Order(id=1, total_price=0.0)

    def query_side_effect(model_class):
        mock_query = mocker.Mock()
        if model_class == menu_model.Menu:
            mock_query.filter.return_value.first.return_value = mock_menu_item
        elif model_class == orders_model.Order:
            mock_query.filter.return_value.first.return_value = mock_order
        return mock_query

    db_session.query.side_effect = query_side_effect

    created_detail = controller.create(db_session, order_detail_object)

    assert created_detail is not None
    assert created_detail.order_id == 1
    assert created_detail.menu_id == 1
    assert created_detail.amount == 2
    assert mock_order.total_price == 20.0
    assert db_session.add.called
    assert db_session.commit.called


def test_read_all_order_details(db_session):
    mock_details = [
        model.OrderDetail(id=1, order_id=1, menu_id=1, amount=2),
        model.OrderDetail(id=2, order_id=1, menu_id=2, amount=1)
    ]
    db_session.query.return_value.all.return_value = mock_details

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2


def test_read_one_order_detail(db_session):
    mock_detail = model.OrderDetail(id=1, order_id=1, menu_id=1, amount=2)
    db_session.query.return_value.filter.return_value.first.return_value = mock_detail

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.amount == 2


def test_update_order_detail(db_session):
    mock_detail = model.OrderDetail(id=1, order_id=1, menu_id=1, amount=2)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_detail

    update_data = schema.OrderDetailUpdate(amount=3)
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert mock_query.update.called
    assert db_session.commit.called


def test_delete_order_detail(db_session):
    mock_detail = model.OrderDetail(id=1, order_id=1, menu_id=1, amount=2)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_detail

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert mock_query.delete.called
    assert db_session.commit.called


def test_read_one_order_detail_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.read_one(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_update_order_detail_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = schema.OrderDetailUpdate(amount=5)
    with pytest.raises(HTTPException) as exc_info:
        controller.update(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_delete_order_detail_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"

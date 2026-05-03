from fastapi.testclient import TestClient
from fastapi import HTTPException
from ..controllers import orders as controller
from ..main import app
import pytest
from ..models import orders as model
from ..schemas import orders as schema
from decimal import Decimal

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order(db_session):
    # Create a sample order
    order_data = {
        "customers_id": 1,
        "customers_name": "John Doe",
        "description": "Test order",
        "customers_email": "johndoe@gmail.com",
        "customers_phone": "123-456-7890",
        "order_type": "Takeout",
        "order_status": "Placed",
        "total_price": 10.0
    }

    order_object = model.Order(**order_data)

    # Call the create function
    created_order = controller.create(db_session, order_object)

    # Assertions
    assert created_order is not None
    assert created_order.customers_name == "John Doe"
    assert created_order.description == "Test order"
    assert db_session.add.called
    assert db_session.commit.called


def test_read_all_orders(db_session):
    mock_orders = [
        model.Order(id=1, customers_name="John Doe"),
        model.Order(id=2, customers_name="Jane Doe")
    ]
    db_session.query.return_value.all.return_value = mock_orders

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].customers_name == "John Doe"


def test_read_one_order(db_session):
    mock_order = model.Order(id=1, customers_name="John Doe")
    db_session.query.return_value.filter.return_value.first.return_value = mock_order

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.customers_name == "John Doe"


def test_read_one_order_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.read_one(db_session, 999)
    assert exc_info.value.status_code == 404


def test_read_one_by_tracking_number(db_session):
    mock_order = model.Order(id=1, tracking_number="TRK-123")
    db_session.query.return_value.filter.return_value.first.return_value = mock_order

    result = controller.read_one_by_tracking_number(db_session, "TRK-123")

    assert result is not None
    assert result.tracking_number == "TRK-123"


def test_update_order(db_session, mocker):
    mock_order = model.Order(id=1, customers_name="John Doe")
    query_mock = db_session.query.return_value.filter.return_value
    query_mock.first.return_value = mock_order

    request_mock = mocker.Mock()
    request_mock.dict.return_value = {"customers_name": "Johnny Doe"}

    result = controller.update(db_session, 1, request_mock)

    assert result is not None
    assert query_mock.update.called
    assert db_session.commit.called


def test_delete_order(db_session):
    mock_order = model.Order(id=1)
    query_mock = db_session.query.return_value.filter.return_value
    query_mock.first.return_value = mock_order

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert query_mock.delete.called
    assert db_session.commit.called


def test_get_item_revenue(db_session, mocker):
    # Mock the dish (Menu item)
    mock_dish = mocker.Mock()
    mock_dish.dish_name = "Pizza"
    mock_dish.price = Decimal("10.00")

    # Mock the OrderDetails (Sold items)
    mock_detail = mocker.Mock()
    mock_detail.amount = 2  # Sold 2 pizzas

    # Setup query behavior
    # Note: get_item_revenue does a join and multiple queries
    def query_side_effect(model_class):
        mock_query = mocker.Mock()
        if "OrderDetail" in str(model_class):
            mock_query.join.return_value.filter.return_value.all.return_value = [mock_detail]
        elif "Menu" in str(model_class):
            mock_query.filter.return_value.first.return_value = mock_dish
        return mock_query

    db_session.query.side_effect = query_side_effect

    result = controller.get_item_revenue(db_session, menu_id=1)

    assert result["menu_item"] == "Pizza"
    assert result["total_revenue"] == Decimal("20.00")  # 2 * 10.00
    assert result["total_sold"] == 2


def test_get_total_revenue(db_session):
    # Mock multiple orders with prices
    mock_orders = [
        model.Order(total_price=Decimal("50.00")),
        model.Order(total_price=Decimal("30.00"))
    ]
    db_session.query.return_value.all.return_value = mock_orders

    result = controller.get_total_revenue(db_session)

    assert result["total_revenue"] == Decimal("80.00")
    assert result["order_count"] == 2


def test_create_order_with_promo(db_session, mocker):
    from ..models import promotions as promo_model
    from datetime import datetime, timedelta

    # Mock promotion
    mock_promo = promo_model.Promotions(
        promotions_name="SAVE10",
        promotions_discount=10,
        expiration_date=datetime.now() + timedelta(days=1)
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_promo

    new_order = {
        "customers_id": 1,
        "customers_name": "John Doe",
        "customers_email": "johndoe@gmail.com",
        "customers_phone": "123-456-7890",
        "order_type": "Dine-in",
        "order_status": "Placed",
        "total_price": 100.0,
        "promo_code": "SAVE10"
    }
    order_data = schema.OrderCreate(**new_order)

    created_order = controller.create(db_session, order_data)

    # 10% discount on 100.0 should be 90.0
    assert created_order.total_price == 90.0


def test_get_unpopular_dishes(db_session, mocker):
    # Mock results for the aggregated query
    mock_result1 = mocker.Mock()
    mock_result1.id = 1
    mock_result1.dish_name = "Liver"
    mock_result1.total_sold = 0

    mock_result2 = mocker.Mock()
    mock_result2.id = 2
    mock_result2.dish_name = "Brussels Sprouts"
    mock_result2.total_sold = 1

    mock_results = [mock_result1, mock_result2]
    
    # Mock the complex query chain
    db_session.query.return_value.outerjoin.return_value.group_by.return_value.having.return_value.order_by.return_value.all.return_value = mock_results

    result = controller.get_unpopular_dishes(db_session, threshold=3)

    assert len(result) == 2
    assert result[0]["dish_name"] == "Liver"
    assert result[0]["total_sold"] == 0

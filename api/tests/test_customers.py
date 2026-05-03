from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from ..controllers import customers as controller
from ..main import app
import pytest
from ..models import customers as model
from ..models import orders as order_model
from ..models import favorite_orders as fav_model
from ..models import rewards as reward_model
from ..schemas import customers as schema
from datetime import datetime, date
from ..dependencies.security import hash_password, verify_password

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
        "address": "123 Main St",
        "password": "securepassword123"
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
        model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass")),
        model.Customers(id=2, first_name="Jane", last_name="Doe", password=hash_password("pass"))
    ]
    db_session.query.return_value.all.return_value = mock_customers

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"


def test_read_one_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"


def test_update_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_customer

    update_data = schema.CustomersUpdate(first_name="Johnny")
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert mock_query.update.called
    assert db_session.commit.called


def test_delete_customer(db_session):
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
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


# Tests for Password Change
def test_change_password(db_session):
    """Test password change functionality"""
    hashed_password = hash_password("oldpassword")
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hashed_password
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.change_password(
        db=db_session,
        customer_id=1,
        old_password="oldpassword",
        new_password="newpassword123"
    )

    assert result is not None
    assert db_session.commit.called
    assert db_session.refresh.called


def test_change_password_invalid_old_password(db_session):
    """Test password change with invalid old password"""
    hashed_password = hash_password("oldpassword")
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hashed_password
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    with pytest.raises(HTTPException) as exc_info:
        controller.change_password(
            db=db_session,
            customer_id=1,
            old_password="wrongpassword",
            new_password="newpassword123"
        )
    assert exc_info.value.status_code == 401
    assert "Invalid old password" in exc_info.value.detail


def test_change_password_customer_not_found(db_session):
    """Test password change when customer not found"""
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.change_password(
            db=db_session,
            customer_id=999,
            old_password="oldpassword",
            new_password="newpassword123"
        )
    assert exc_info.value.status_code == 404


# Tests for Order History
def test_get_order_history(db_session):
    """Test getting order history"""
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_orders = [
        order_model.Order(id=1, customers_id=1, tracking_number="TRK001", order_status="Completed"),
        order_model.Order(id=2, customers_id=1, tracking_number="TRK002", order_status="Pending")
    ]
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    db_session.query.return_value.filter.return_value.all.return_value = mock_orders

    result = controller.get_order_history(db=db_session, customer_id=1)

    assert len(result) == 2
    assert result[0].tracking_number == "TRK001"
    assert result[1].tracking_number == "TRK002"


# Tests for Favorite Orders
def test_add_favorite_order(db_session):
    """Test adding a favorite order"""
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_order = order_model.Order(id=1, customers_id=1, tracking_number="TRK001", order_status="Completed")
    
    def mock_query_filter(query_obj):
        if hasattr(query_obj, 'first'):
            return type('obj', (object,), {'first': lambda: mock_customer})()
        if hasattr(query_obj, 'all'):
            return type('obj', (object,), {'all': lambda: []})()
        return mock_query_filter
    
    db_session.query.return_value.filter.return_value.first.side_effect = [mock_customer, mock_order, None]
    
    result = controller.add_favorite_order(db=db_session, customer_id=1, order_id=1)

    assert result is not None
    assert db_session.add.called
    assert db_session.commit.called


def test_get_favorite_orders(db_session):
    """Test getting favorite orders"""
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_favorites = [
        fav_model.FavoriteOrder(id=1, customer_id=1, order_id=1),
        fav_model.FavoriteOrder(id=2, customer_id=1, order_id=2)
    ]
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    db_session.query.return_value.filter.return_value.all.return_value = mock_favorites

    result = controller.get_favorite_orders(db=db_session, customer_id=1)

    assert len(result) == 2
    assert result[0].order_id == 1
    assert result[1].order_id == 2


# Tests for Rewards Program
def test_add_reward_points(db_session):
    """Test adding reward points"""
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        reward_points=0
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.add_reward_points(
        db=db_session,
        customer_id=1,
        points=100,
        reward_type="purchase"
    )

    assert result is not None
    assert db_session.add.called
    assert db_session.commit.called


def test_redeem_reward_points(db_session):
    """Test redeeming reward points"""
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        reward_points=100
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.redeem_reward_points(
        db=db_session,
        customer_id=1,
        points_to_redeem=50
    )

    assert result is not None
    assert db_session.add.called
    assert db_session.commit.called


def test_redeem_insufficient_points(db_session):
    """Test redeeming with insufficient points"""
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        reward_points=30
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    with pytest.raises(HTTPException) as exc_info:
        controller.redeem_reward_points(
            db=db_session,
            customer_id=1,
            points_to_redeem=50
        )
    assert exc_info.value.status_code == 400
    assert "Insufficient reward points" in exc_info.value.detail


def test_check_birthday_reward(db_session):
    """Test birthday reward"""
    today = date.today()
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        birthday=date(1990, today.month, today.day),
        reward_points=0
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer

    result = controller.check_birthday_reward(db=db_session, customer_id=1)

    assert result is not None
    assert db_session.add.called
    assert db_session.commit.called


def test_check_birthday_reward_not_today(db_session):
    """Test birthday reward when it's not the birthday"""
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        birthday=date(1990, 1, 1),
        reward_points=0
    )
    with pytest.raises(HTTPException) as exc_info:
        controller.check_birthday_reward(db=db_session, customer_id=1)
    assert exc_info.value.status_code == 400
    assert "Today is not the customer's birthday" in exc_info.value.detail

def test_delete_customer_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"
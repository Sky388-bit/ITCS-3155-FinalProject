from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from decimal import Decimal
from ..controllers import menu as controller
from ..main import app
import pytest
from ..models import menu as model
from ..schemas import menu as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_menu_item(db_session):
    # Create a sample item
    new_item = {
        "dish_name": "Tomato Soup",
        "dish_description": "Soup that pairs well with grilled cheese",
        "price": Decimal(5.20),
        "calories": 7000,
        "category": "Soup"
    }

    menu_item = schema.MenuCreate(**new_item)

    # Call the create function
    created_item = controller.create(db_session, menu_item)

    # Assertions
    assert created_item is not None
    assert created_item.dish_name == "Tomato Soup"
    assert created_item.dish_description == "Soup that pairs well with grilled cheese"
    assert created_item.price == Decimal(5.20)
    assert created_item.calories == 7000
    assert created_item.category == "Soup"


def test_read_all_menu(db_session):
    mock_items = [
        model.Menu(id=1, dish_name="Pizza", price=Decimal("12.00")),
        model.Menu(id=2, dish_name="Burger", price=Decimal("8.00"))
    ]
    db_session.query.return_value.all.return_value = mock_items

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].dish_name == "Pizza"
    assert result[1].dish_name == "Burger"


def test_read_one_menu_item(db_session):
    mock_item = model.Menu(id=1, dish_name="Pizza", price=Decimal("12.00"))
    db_session.query.return_value.filter.return_value.first.return_value = mock_item

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.dish_name == "Pizza"


def test_read_one_menu_item_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        controller.read_one(db_session, 999)
    assert excinfo.value.status_code == 404


def test_update_menu_item(db_session):
    mock_item = model.Menu(id=1, dish_name="Pizza", price=Decimal("12.00"))
    db_session.query.return_value.filter.return_value.first.return_value = mock_item

    update_data = schema.MenuUpdate(price=Decimal("15.00"))
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert result.price == Decimal("15.00")
    assert db_session.commit.called


def test_update_menu_item_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = schema.MenuUpdate(price=Decimal("15.00"))
    with pytest.raises(HTTPException) as excinfo:
        controller.update(db_session, 999, update_data)
    assert excinfo.value.status_code == 404


def test_delete_menu_item(db_session):
    mock_item = model.Menu(id=1, dish_name="Pizza")
    db_session.query.return_value.filter.return_value.first.return_value = mock_item

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert db_session.delete.called
    assert db_session.commit.called


def test_delete_menu_item_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        controller.delete(db_session, 999)
    assert excinfo.value.status_code == 404
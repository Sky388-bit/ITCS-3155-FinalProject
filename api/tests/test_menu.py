from fastapi.testclient import TestClient
from ..controllers import menu as controller
from ..main import app
import pytest
from ..models import menu as model

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order(db_session):
    # Create a sample order
    new_item = {
        "dish_name": "Tomato Soup",
        "dish_description": "Soup that pairs well with grilled cheese",
        "price": 5.20,
        "calories": 7000,
        "category": "Soup"
    }

    menu_item = model.Menu(**new_item)

    # Call the create function
    created_item = controller.create(db_session, menu_item)

    # Assertions
    assert created_item is not None
    assert created_item.dish_name == "Tomato Soup"
    assert created_item.dish_description == "Soup that pairs well with grilled cheese"
    assert created_item.price == 5.20
    assert created_item.calories == 7000
    assert created_item.category == "Soup"
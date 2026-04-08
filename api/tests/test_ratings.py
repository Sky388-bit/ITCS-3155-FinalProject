from fastapi.testclient import TestClient
from ..controllers import ratings as controller
from ..main import app
import pytest
from ..models import ratings as model

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_ratings(db_session):
    # Create a sample ratings
    ratings_data = {
        "customer_name": "Test",
        "review_text": "Test rating",
        "rating": 5
    }

    ratings_object = model.Ratings(**ratings_data)

    # Call the create function
    created_ratings = controller.create(db_session, ratings_object)

    # Assertions
    assert created_ratings is not None
    assert created_ratings.customer_name == "John Doe"
    assert created_ratings.description == "Test ratings"

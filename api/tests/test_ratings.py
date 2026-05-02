from fastapi.testclient import TestClient
from fastapi import HTTPException
from ..controllers import ratings as controller
from ..main import app
import pytest
from ..models import ratings as model
from ..schemas import ratings as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_ratings(db_session):
    # Create a sample ratings
    ratings_data = {
        "customers_id": 1,
        "menu_id": 1,
        "customers_name": "John Doe",
        "review_text": "Test ratings",
        "rating": 5
    }

    ratings_object = schema.RatingsCreate(**ratings_data)

    # Call the create function
    created_ratings = controller.create(db_session, ratings_object)

    # Assertions
    assert created_ratings is not None
    assert created_ratings.customers_name == "John Doe"
    assert created_ratings.review_text == "Test ratings"
    assert db_session.add.called
    assert db_session.commit.called


def test_read_all_ratings(db_session):
    mock_ratings = [
        model.Ratings(id=1, customers_name="John Doe", rating=5),
        model.Ratings(id=2, customers_name="Jane Doe", rating=4)
    ]
    db_session.query.return_value.all.return_value = mock_ratings

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].customers_name == "John Doe"
    assert result[1].customers_name == "Jane Doe"


def test_read_one_rating(db_session):
    mock_rating = model.Ratings(id=1, customers_name="John Doe", rating=5)
    db_session.query.return_value.filter.return_value.first.return_value = mock_rating

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.customers_name == "John Doe"


def test_read_one_rating_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.read_one(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_update_rating(db_session, mocker):
    mock_rating = model.Ratings(id=1, review_text="Good")
    query_mock = db_session.query.return_value.filter.return_value
    query_mock.first.return_value = mock_rating

    request_mock = mocker.Mock()
    request_mock.dict.return_value = {"review_text": "Great"}

    result = controller.update(db_session, 1, request_mock)

    assert result is not None
    assert query_mock.update.called
    assert db_session.commit.called


def test_update_rating_not_found(db_session, mocker):
    db_session.query.return_value.filter.return_value.first.return_value = None

    request_mock = mocker.Mock()
    with pytest.raises(HTTPException) as exc_info:
        controller.update(db_session, 999, request_mock)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_delete_rating(db_session):
    mock_rating = model.Ratings(id=1)
    query_mock = db_session.query.return_value.filter.return_value
    query_mock.first.return_value = mock_rating

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert query_mock.delete.called
    assert db_session.commit.called


def test_delete_rating_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"

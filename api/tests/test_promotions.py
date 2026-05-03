from fastapi.testclient import TestClient
from fastapi import HTTPException
from ..controllers import promotions as controller
from ..main import app
import pytest
from ..models import promotions as model
from ..schemas import promotions as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_promotion(db_session):
    promotion_data = {
        "promotions_discount": 10,
        "promotions_name": "Winter Sale"
    }
    promotion_object = schema.PromotionsCreate(**promotion_data)
    created_promotion = controller.create(db_session, promotion_object)

    assert created_promotion is not None
    assert created_promotion.promotions_name == "Winter Sale"
    assert created_promotion.promotions_discount == 10
    assert db_session.add.called
    assert db_session.commit.called


def test_create_promotion_with_expiration(db_session):
    from datetime import datetime, timedelta
    expiration = datetime.now() + timedelta(days=7)
    promotion_data = {
        "promotions_discount": 20,
        "promotions_name": "Weekly Special",
        "expiration_date": expiration
    }
    promotion_object = schema.PromotionsCreate(**promotion_data)
    created_promotion = controller.create(db_session, promotion_object)

    assert created_promotion.expiration_date == expiration


def test_read_all_promotions(db_session):
    mock_promotions = [
        model.Promotions(id=1, promotions_name="Sale 1", promotions_discount=10),
        model.Promotions(id=2, promotions_name="Sale 2", promotions_discount=20)
    ]
    db_session.query.return_value.all.return_value = mock_promotions

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].promotions_name == "Sale 1"
    assert result[1].promotions_name == "Sale 2"


def test_read_one_promotion(db_session):
    mock_promotion = model.Promotions(id=1, promotions_name="Sale 1", promotions_discount=10)
    db_session.query.return_value.filter.return_value.first.return_value = mock_promotion

    result = controller.read_one(db_session, 1)

    assert result is not None
    assert result.id == 1
    assert result.promotions_name == "Sale 1"


def test_update_promotion(db_session):
    mock_promotion = model.Promotions(id=1, promotions_name="Sale 1", promotions_discount=10)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_promotion

    update_data = schema.PromotionsUpdate(promotions_name="New Sale", promotions_discount=15)
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert mock_query.update.called
    assert db_session.commit.called


def test_delete_promotion(db_session):
    mock_promotion = model.Promotions(id=1, promotions_name="Sale 1", promotions_discount=10)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = mock_promotion

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert mock_query.delete.called
    assert db_session.commit.called


def test_read_one_promotion_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.read_one(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_update_promotion_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = schema.PromotionsUpdate(promotions_name="New Sale")
    with pytest.raises(HTTPException) as exc_info:
        controller.update(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"


def test_delete_promotion_not_found(db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.delete(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Id not found!"

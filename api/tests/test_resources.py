from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from ..controllers import resources as controller
from ..main import app
import pytest
from ..models import resources as model
from ..schemas import resources as schema

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_resource(db_session):
    # Create a sample resource
    new_resource = {
        "item": "Flour",
        "amount": 100,
        "min_threshold": 20
    }

    resource_data = schema.ResourceCreate(**new_resource)

    # Call the create function
    created_resource = controller.create(db_session, resource_data)

    # Assertions
    assert created_resource is not None
    assert created_resource.item == "Flour"
    assert created_resource.amount == 100
    assert created_resource.min_threshold == 20


def test_read_all_resources(db_session):
    mock_resources = [
        model.Resource(id=1, item="Flour", amount=100, min_threshold=20),
        model.Resource(id=2, item="Sugar", amount=10, min_threshold=30)
    ]
    db_session.query.return_value.all.return_value = mock_resources

    result = controller.read_all(db_session)

    assert len(result) == 2
    assert result[0].item == "Flour"
    assert result[1].item == "Sugar"


def test_get_low_stock(db_session):
    mock_low_stock = [
        model.Resource(id=2, item="Sugar", amount=10, min_threshold=30)
    ]
    # Simulate the filter query for low stock
    db_session.query.return_value.filter.return_value.all.return_value = mock_low_stock

    result = controller.get_low_stock(db_session)

    assert len(result) == 1
    assert result[0].item == "Sugar"
    assert result[0].amount < result[0].min_threshold


def test_update_resource(db_session):
    mock_resource = model.Resource(id=1, item="Flour", amount=100, min_threshold=20)
    db_session.query.return_value.filter.return_value.first.return_value = mock_resource

    update_data = schema.ResourceUpdate(amount=50)
    result = controller.update(db_session, 1, update_data)

    assert result is not None
    assert result.amount == 50
    assert db_session.commit.called


def test_delete_resource(db_session):
    mock_resource = model.Resource(id=1, item="Flour")
    db_session.query.return_value.filter.return_value.first.return_value = mock_resource

    response = controller.delete(db_session, 1)

    assert response.status_code == 204
    assert db_session.commit.called

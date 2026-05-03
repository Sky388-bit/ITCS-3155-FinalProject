from fastapi.testclient import TestClient
from fastapi.exceptions import HTTPException
from ..controllers import rewards as controller
from ..main import app
import pytest
from ..models import customers as model
from ..models import rewards as reward_model
from ..dependencies.security import hash_password

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_get_customer_rewards(db_session):
    """Test getting all rewards for a customer"""
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_rewards = [
        reward_model.Reward(id=1, customer_id=1, points_earned=100, reward_type="purchase"),
        reward_model.Reward(id=2, customer_id=1, points_earned=50, reward_type="birthday")
    ]
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    db_session.query.return_value.filter.return_value.all.return_value = mock_rewards

    result = controller.get_customer_rewards(db=db_session, customer_id=1)

    assert len(result) == 2
    assert result[0].points_earned == 100
    assert result[1].points_earned == 50


def test_get_unredeemed_rewards(db_session):
    """Test getting unredeemed rewards for a customer"""
    mock_customer = model.Customers(id=1, first_name="John", last_name="Doe", password=hash_password("pass"))
    mock_unredeemed = [
        reward_model.Reward(id=1, customer_id=1, points_earned=100, reward_type="purchase", is_redeemed=False)
    ]
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    db_session.query.return_value.filter.return_value.all.return_value = mock_unredeemed

    result = controller.get_unredeemed_rewards(db=db_session, customer_id=1)

    assert len(result) == 1
    assert result[0].is_redeemed == False


def test_get_reward_summary(db_session):
    """Test getting reward summary for a customer"""
    mock_customer = model.Customers(
        id=1,
        first_name="John",
        last_name="Doe",
        password=hash_password("pass"),
        reward_points=250
    )
    mock_rewards = [
        reward_model.Reward(id=1, customer_id=1, points_earned=100, reward_type="purchase", is_redeemed=False),
        reward_model.Reward(id=2, customer_id=1, points_earned=150, reward_type="birthday", is_redeemed=False)
    ]
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_customer
    db_session.query.return_value.filter.return_value.all.return_value = mock_rewards

    result = controller.get_reward_summary(db=db_session, customer_id=1)

    assert result["customer_id"] == 1
    assert result["current_points"] == 250
    assert result["total_rewards"] == 2


def test_get_customer_rewards_not_found(db_session):
    """Test getting rewards when customer not found"""
    db_session.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        controller.get_customer_rewards(db=db_session, customer_id=999)
    assert exc_info.value.status_code == 404

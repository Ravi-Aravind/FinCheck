import pytest
from app import create_app


@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite3")})


@pytest.fixture
def client(app):
    return app.test_client()


def transaction(**overrides):
    data = {"transaction_id": "TEST-001", "amount": 2500, "location": "India", "transaction_type": "PURCHASE"}
    data.update(overrides)
    return data

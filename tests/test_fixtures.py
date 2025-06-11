import pytest
import json

@pytest.fixture(scope="module")
def user_fixture():
    with open("users.json") as f:
        return json.load(f)

def test_user_count(user_fixture):
    assert len(user_fixture) == 20

def test_first_user(user_fixture):
    assert user_fixture[0]["username"] == "testuser1"

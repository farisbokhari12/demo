try:
    import error_handling  # installs global excepthook and helpers
except Exception:
    pass

import pytest
from src.api_client import UserAPIClient

@pytest.fixture
def api_client():
    return UserAPIClient(base_url='http://example.com', api_key='test')


def test_new_feature(api_client):
    response = api_client.new_feature({'key': 'value'})
    assert response['status'] == 'success'

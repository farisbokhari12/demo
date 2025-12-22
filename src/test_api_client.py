try:
    import error_handling  # installs global excepthook and helpers
except Exception:
    pass

import pytest
from src.api_client import UserAPIClient

@pytest.fixture
def api_client():
    return UserAPIClient(base_url='http://example.com', api_key='test')


def test_new_feature(api_client, monkeypatch):
    class DummyResponse:
        def __init__(self):
            self.status_code = 200
            self.url = api_client.base_url + '/new-feature'
        def raise_for_status(self):
            return None
        def json(self):
            return {'status': 'success'}

    def fake_request(method, url, headers=None, timeout=None, **kwargs):
        return DummyResponse()

    monkeypatch.setattr('requests.request', fake_request)

    response = api_client.new_feature({'key': 'value'})
    assert response['status'] == 'success'

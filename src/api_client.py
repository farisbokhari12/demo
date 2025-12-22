import requests
import logging
from typing import Dict, List, Optional
from error_handling import handle_exceptions

logger = logging.getLogger(__name__)

class UserAPIClient:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException:
            logger.exception("Request failed: %s %s", method, url)
            raise

    def new_feature(self, data: Dict) -> Dict:
        """Handles the new feature request."""
        response = self._make_request('POST', '/new-feature', json=data)
        try:
            return response.json()
        except ValueError:
            logger.exception("Failed to decode JSON response from %s", response.url)
            raise

    # Existing methods...

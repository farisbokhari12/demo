import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class UserAPIClient:
    """Client for interacting with User Management API"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method, url, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            raise APIError(f"API request failed: {e}")
    
    def get_user(self, user_id: str, use_cache: bool = True) -> Dict:
        """Get user by ID"""
        cache_key = f"user:{user_id}"
        
        # Check cache if enabled
        if use_cache and cache_key in self._cache:
            cached_time = self._cache_timestamps.get(cache_key, 0)
            if time.time() - cached_time < self._cache_ttl:
                return self._cache[cache_key]
        
        response = self._make_request('GET', f'/users/{user_id}')
        user_data = response.json()
        
        # Cache the response
        if use_cache:
            self._cache[cache_key] = user_data
            self._cache_timestamps[cache_key] = time.time()
        
        return user_data
    
    def create_user(self, email: str, name: str, role: str = 'user') -> Dict:
        """Create a new user"""
        if '@' not in email or '.' not in email.split('@')[1]:
            raise ValueError("Invalid email format")
        
        payload = {
            'email': email,
            'name': name,
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        
        response = self._make_request('POST', '/users', json=payload)
        return response.json()
    
    def update_user(self, user_id: str, **updates) -> Dict:
        """Update user information"""
        if not updates:
            raise ValueError("No updates provided")
        
        response = self._make_request('PATCH', f'/users/{user_id}', json=updates)
        user_data = response.json()
        
        # Invalidate cache for updated user
        cache_key = f"user:{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            if cache_key in self._cache_timestamps:
                del self._cache_timestamps[cache_key]
        
        return user_data
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        response = self._make_request('DELETE', f'/users/{user_id}')
        
        # Invalidate cache
        cache_key = f"user:{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]
            if cache_key in self._cache_timestamps:
                del self._cache_timestamps[cache_key]
        
        return response.status_code == 204 or response.json().get('deleted', False)
    
    def list_users(self, page: int = 1, per_page: int = 20, role: Optional[str] = None) -> Dict:
        """List users with pagination"""
        if page < 1:
            raise ValueError("Page must be >= 1")
        
        params = {'page': page, 'per_page': per_page}
        if role:
            params['role'] = role
        
        response = self._make_request('GET', '/users', params=params)
        data = response.json()
        
        return {
            'users': data.get('data', []),
            'total': data.get('total', 0),
            'page': page,
            'per_page': per_page,
            'total_pages': (data.get('total', 0) + per_page - 1) // per_page
        }
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict]:
        """Search users by name or email"""
        if not query or len(query.strip()) == 0:
            raise ValueError("Search query cannot be empty")
        
        params = {'q': query.strip(), 'limit': limit}
        response = self._make_request('GET', '/users/search', params=params)
        return response.json().get('results', [])
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        user = self.get_user(user_id)
        return user.get('permissions', [])
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache = {}
        self._cache_timestamps = {}

class APIError(Exception):
    """Base exception for API errors"""
    pass

class AuthenticationError(APIError):
    """Authentication failed"""
    pass

class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass
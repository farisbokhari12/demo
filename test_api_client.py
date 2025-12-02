"""Tests for UserAPIClient"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import time
from src.api_client import UserAPIClient, APIError, AuthenticationError, RateLimitError


@pytest.fixture
def mock_client():
    """Create a mock API client"""
    with patch('src.api_client.requests.Session') as mock_session:
        client = UserAPIClient('https://api.example.com', 'test-api-key')
        client.session = mock_session.return_value
        return client


def test_get_user_success(mock_client):
    """Test successful user retrieval"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'id': '123',
        'email': 'test@example.com',
        'name': 'Test User',
        'role': 'user'
    }
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    user = mock_client.get_user('123', use_cache=False)
    
    assert user['id'] == '123'
    assert user['email'] == 'test@example.com'
    mock_client.session.request.assert_called_once()


def test_get_user_caching(mock_client):
    """Test user caching functionality"""
    mock_response = Mock()
    mock_response.json.return_value = {'id': '123', 'name': 'Test User'}
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    # First call should hit API
    user1 = mock_client.get_user('123')
    assert mock_client.session.request.call_count == 1
    
    # Second call should use cache (within TTL)
    user2 = mock_client.get_user('123')
    assert mock_client.session.request.call_count == 1  # Should still be 1
    assert user1 == user2


def test_get_user_cache_expiration(mock_client):
    """Test that cache expires after TTL"""
    mock_response = Mock()
    mock_response.json.return_value = {'id': '123', 'name': 'Test User'}
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    # First call
    mock_client.get_user('123')
    assert mock_client.session.request.call_count == 1
    
    # Simulate cache expiration by moving time forward
    original_time = time.time
    time.time = lambda: original_time() + 400  # 400 seconds > 300 TTL
    
    try:
        # Second call should hit API again after cache expires
        mock_client.get_user('123')
        # BUG: This test will fail because cache expiration check is wrong
        # The bug is: cached_time + self._cache_ttl > time.time()
        # Should be: time.time() - cached_time < self._cache_ttl
        assert mock_client.session.request.call_count == 2
    finally:
        time.time = original_time


def test_create_user_success(mock_client):
    """Test successful user creation"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'id': '456',
        'email': 'new@example.com',
        'name': 'New User'
    }
    mock_response.status_code = 201
    mock_client.session.request.return_value = mock_response
    
    user = mock_client.create_user('new@example.com', 'New User')
    
    assert user['id'] == '456'
    mock_client.session.request.assert_called_once()


def test_create_user_invalid_email(mock_client):
    """Test user creation with invalid email"""
    with pytest.raises(ValueError, match="Invalid email format"):
        mock_client.create_user('invalid-email', 'Test User')


def test_update_user_success(mock_client):
    """Test successful user update"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'id': '123',
        'name': 'Updated Name'
    }
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    user = mock_client.update_user('123', name='Updated Name')
    
    assert user['name'] == 'Updated Name'
    mock_client.session.request.assert_called_once()


def test_delete_user_success(mock_client):
    """Test successful user deletion"""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_client.session.request.return_value = mock_response
    
    result = mock_client.delete_user('123')
    
    assert result is True
    mock_client.session.request.assert_called_once()


def test_list_users_pagination(mock_client):
    """Test listing users with pagination"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'data': [{'id': '1'}, {'id': '2'}],
        'total': 50
    }
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    result = mock_client.list_users(page=1, per_page=20)
    
    assert len(result['users']) == 2
    assert result['total'] == 50
    assert result['page'] == 1


def test_search_users_success(mock_client):
    """Test user search"""
    mock_response = Mock()
    mock_response.json.return_value = {
        'results': [{'id': '1', 'name': 'John'}]
    }
    mock_response.status_code = 200
    mock_client.session.request.return_value = mock_response
    
    results = mock_client.search_users('John')
    
    assert len(results) == 1
    assert results[0]['name'] == 'John'


def test_authentication_error(mock_client):
    """Test handling of authentication errors"""
    mock_response = Mock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_client.session.request.return_value = mock_response
    
    with pytest.raises(AuthenticationError):
        mock_client.get_user('123', use_cache=False)


def test_rate_limit_error(mock_client):
    """Test handling of rate limit errors"""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_client.session.request.return_value = mock_response
    
    with pytest.raises(RateLimitError):
        mock_client.get_user('123', use_cache=False)


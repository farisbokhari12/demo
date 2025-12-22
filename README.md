# Python API Client Project

## Overview

This project is a Python-based API client designed to interact with a user management system. It includes functionality for creating, updating, deleting, and retrieving user information, as well as handling authentication and rate limiting errors.

## Structure

- **`src/api_client.py`**: Contains the `UserAPIClient` class for managing API interactions and custom exceptions for error handling.
- **`src/hello_world.py`**: A simple module with a `hello_world` function.
- **`src/test_api_client.py`**: Test cases for the API client using pytest.
- **`src/test_hello_world.py`**: Test cases for the `hello_world` function using unittest.

## Installation

1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt`.

## Usage

- Import the `UserAPIClient` class from `api_client.py` to interact with the API.
- Run tests using `pytest` for `test_api_client.py` and `unittest` for `test_hello_world.py`.

## Testing

To run the tests, execute:

```bash
pytest src/test_api_client.py
python -m unittest src/test_hello_world.py
```

## License

This project is licensed under the MIT License.

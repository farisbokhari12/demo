try:
    import error_handling  # installs global excepthook and helpers
except Exception:
    pass

import unittest
from src.hello_world import hello_world

class TestHelloWorld(unittest.TestCase):
    def test_hello_world(self):
        self.assertEqual(hello_world(), "Hello, World!")

if __name__ == '__main__':
    unittest.main()

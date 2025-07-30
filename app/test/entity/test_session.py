import unittest
from time import time
from src.entity.session import Session


class TestSession(unittest.TestCase):

    def setUp(self):
        self.token = "test_token"
        self.refresh_token = "test_refresh_token"
        self.session = Session(self.token, self.refresh_token)

    def test_initialization(self):
        """Test that the session is initialized correctly."""
        # Assert
        self.assertEqual(self.session.token, self.token)
        self.assertEqual(self.session.refresh_token, self.refresh_token)
        self.assertIsNotNone(self.session.token_generated_at)
        self.assertIsNotNone(self.session.refresh_token_generated_at)

    def test_is_token_expired_not_expired(self):
        # Assert
        self.assertFalse(self.session.is_token_expired())

    def test_is_token_expired_expired(self):
        """Test that the token is expired when beyond the expiration time."""
        # Arrange
        self.session.token_generated_at = time() - (91 * 60)  # Simulate expiration
        # Assert
        self.assertTrue(self.session.is_token_expired())

    def test_is_refresh_token_expired_not_expired(self):
        """Test that the refresh token is not expired when within the expiration time."""
        # Assert
        self.assertFalse(self.session.is_refresh_token_expired())

    def test_is_refresh_token_expired_expired(self):
        """Test that the refresh token is expired when beyond the expiration time."""
        # Assert
        self.session.refresh_token_generated_at = time() - (59 * 24 * 60 * 60)  # Simulate expiration
        # Assert
        self.assertTrue(self.session.is_refresh_token_expired())

    def test_get_token(self):
        """Test that the correct token is returned."""
        # Assert
        self.assertEqual(self.session.get_token(), self.token)


if __name__ == '__main__':
    unittest.main()

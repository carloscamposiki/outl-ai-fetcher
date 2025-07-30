import unittest
from unittest.mock import MagicMock, patch
from time import time
from src.adapter.api.token_manager import TokenManager
from src.exception.blue_sky_exception import BlueSkyException


class TestTokenManager(unittest.TestCase):

    def setUp(self):
        self.mock_secrets_manager = MagicMock()
        self.mock_session_secret_name = "mock_session_secret"
        self.mock_credentials_secret_name = "mock_credentials_secret"
        self.mock_session_data = {
            'token': 'mock_token',
            'refresh_token': 'mock_refresh_token',
            'token_generated_at': time(),
            'refresh_token_generated_at': time()
        }
        self.mock_secrets_manager.get_secret.return_value = self.mock_session_data
        self.token_manager = TokenManager(
            secrets_manager=self.mock_secrets_manager,
            session_secret_name=self.mock_session_secret_name,
            blue_sky_credentials_secret_name=self.mock_credentials_secret_name
        )

    def test_get_session_valid_token(self):
        """ Test when the token is valid and not expired """
        # Arrange
        self.token_manager.session.is_token_expired = MagicMock(return_value=False)

        # Act
        session = self.token_manager.get_session()

        # Assert
        self.assertEqual(session.token, 'mock_token')
        self.mock_secrets_manager.get_secret.assert_called_once_with(self.mock_session_secret_name)

    def test_get_session_expired_token(self):
        """ Test when the token is expired but refresh token is valid """
        # Arrange
        self.token_manager.session.is_token_expired = MagicMock(return_value=True)
        self.token_manager.session.is_refresh_token_expired = MagicMock(return_value=False)
        self.token_manager._refresh_session = MagicMock()

        # Act
        session = self.token_manager.get_session()

        # Assert
        self.token_manager._refresh_session.assert_called_once()
        self.assertEqual(session.token, 'mock_token')

    def test_get_session_expired_refresh_token(self):
        """ Test when both token and refresh token are expired """
        # Arrange
        self.token_manager.session.is_token_expired = MagicMock(return_value=True)
        self.token_manager.session.is_refresh_token_expired = MagicMock(return_value=True)
        self.token_manager._generate_new_session = MagicMock()

        # Act
        session = self.token_manager.get_session()

        # Assert
        self.token_manager._generate_new_session.assert_called_once()
        self.assertEqual(session.token, 'mock_token')

    @patch('src.adapter.api.token_manager.requests.post')
    def test_generate_token_success(self, mock_post):
        """ Test successful token generation """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'accessJwt': 'new_mock_token',
            'refreshJwt': 'new_mock_refresh_token'
        }
        mock_post.return_value = mock_response

        # Act
        session = self.token_manager._generate_token(username="user", password="pass")

        # Assert
        self.assertEqual(session.token, 'Bearer new_mock_token')
        self.assertEqual(session.refresh_token, 'Bearer new_mock_refresh_token')

    @patch('src.adapter.api.token_manager.requests.post')
    def test_generate_token_failure(self, mock_post):
        """ Test token generation failure """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        # Act
        with self.assertRaises(BlueSkyException) as context:
            self.token_manager._generate_token(username="user", password="pass")

        # Assert
        self.assertEqual(
            str(context.exception),
            'Failed to generate token: 400 - Bad Request'
        )

    @patch('src.adapter.api.token_manager.requests.post')
    def test_refresh_token_success(self, mock_post):
        """ Test successful token refresh """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'accessJwt': 'refreshed_mock_token',
            'refreshJwt': 'refreshed_mock_refresh_token'
        }
        mock_post.return_value = mock_response

        # Act
        refreshed_data = self.token_manager._refresh_token("mock_refresh_token")

        # Assert
        self.assertEqual(refreshed_data['token'], 'Bearer refreshed_mock_token')
        self.assertEqual(refreshed_data['refresh_token'], 'Bearer refreshed_mock_refresh_token')

    @patch('src.adapter.api.token_manager.requests.post')
    def test_refresh_token_failure(self, mock_post):
        """ Test token refresh failure """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        # Act
        with self.assertRaises(BlueSkyException) as context:
            self.token_manager._refresh_token("mock_refresh_token")

        # Assert
        self.assertEqual(
            str(context.exception),
            'Failed to refresh token: 401 - Unauthorized'
        )


if __name__ == '__main__':
    unittest.main()

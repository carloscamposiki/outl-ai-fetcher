import unittest
from unittest.mock import MagicMock, patch
from src.adapter.aws.secrets_manager import SecretsManager


class TestSecretsManager(unittest.TestCase):

    def setUp(self):
        self.mock_boto3_client = MagicMock()
        with patch('boto3.client', return_value=self.mock_boto3_client):
            self.secrets_manager = SecretsManager()

    def test_get_secret_success(self):
        """ Test when the secret is successfully retrieved """
        # Arrange
        secret_name = "test_secret"
        secret_value = '{"key": "value"}'
        self.mock_boto3_client.get_secret_value.return_value = {'SecretString': secret_value}

        # Act
        result = self.secrets_manager.get_secret(secret_name)

        # Assert
        self.assertEqual(result, {"key": "value"})
        self.mock_boto3_client.get_secret_value.assert_called_once_with(SecretId=secret_name)

    def test_get_secret_no_secret_string(self):
        """ Test when the secret does not contain SecretString """
        # Arrange
        secret_name = "test_secret"
        self.mock_boto3_client.get_secret_value.return_value = {}

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.secrets_manager.get_secret(secret_name)

        self.assertEqual(str(context.exception), "Secret is not in string format.")
        self.mock_boto3_client.get_secret_value.assert_called_once_with(SecretId=secret_name)

    def test_get_secret_failure(self):
        """ Test when retrieving the secret fails """
        # Arrange
        secret_name = "test_secret"
        self.mock_boto3_client.get_secret_value.side_effect = Exception("SecretsManager Error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.secrets_manager.get_secret(secret_name)

        self.assertEqual(str(context.exception), "SecretsManager Error")

    def test_update_secret_success(self):
        """ Test when the secret is successfully updated """
        # Arrange
        secret_name = "test_secret"
        new_secret_value = {"key": "new_value"}

        # Act
        self.secrets_manager.update_secret(secret_name, new_secret_value)

        # Assert
        self.mock_boto3_client.update_secret.assert_called_once_with(
            SecretId=secret_name,
            SecretString='{"key": "new_value"}'
        )

    def test_update_secret_failure(self):
        """ Test when updating the secret fails """
        # Arrange
        secret_name = "test_secret"
        new_secret_value = {"key": "new_value"}
        self.mock_boto3_client.update_secret.side_effect = Exception("SecretsManager Error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.secrets_manager.update_secret(secret_name, new_secret_value)

        self.assertEqual(str(context.exception), "SecretsManager Error")


if __name__ == '__main__':
    unittest.main()

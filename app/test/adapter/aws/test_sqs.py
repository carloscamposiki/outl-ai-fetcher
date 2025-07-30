import unittest
from unittest.mock import MagicMock, patch
from src.adapter.aws.sqs import SqsAdapter


class TestSqsAdapter(unittest.TestCase):

    def setUp(self):
        self.mock_boto3_client = MagicMock()
        self.queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
        with patch('boto3.client', return_value=self.mock_boto3_client):
            self.sqs_adapter = SqsAdapter(queue_url=self.queue_url)

    def test_send_message_success(self):
        """Test when the message is sent successfully"""
        # Arrange
        message = {"key": "value"}
        self.mock_boto3_client.send_message.return_value = {"MessageId": "12345"}

        # Act
        self.sqs_adapter.send_message(message)

        # Assert
        self.mock_boto3_client.send_message.assert_called_once_with(
            QueueUrl=self.queue_url,
            MessageBody='{"key": "value"}'
        )

    def test_send_message_failure(self):
        """Test when sending the message fails"""
        # Arrange
        message = {"key": "value"}
        self.mock_boto3_client.send_message.side_effect = Exception("SQS Error")

        # Act & Assert
        with self.assertRaises(Exception) as context:
            self.sqs_adapter.send_message(message)

        self.assertEqual(str(context.exception), "SQS Error")


if __name__ == '__main__':
    unittest.main()

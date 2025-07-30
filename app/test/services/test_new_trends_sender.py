import unittest
from unittest.mock import MagicMock
from src.services.new_trends_sender import NewTrendsSender
from src.entity.trend import Trend


class TestNewTrendsSender(unittest.TestCase):

    def setUp(self):
        self.mock_sqs_adapter = MagicMock()
        self.new_trends_sender = NewTrendsSender(sqs_adapter=self.mock_sqs_adapter)

    def test_send_no_new_trends(self):
        """ Test when no new trends are provided"""
        # Act
        self.new_trends_sender.send({})

        # Assert
        self.mock_sqs_adapter.send_message.assert_not_called()

    def test_send_with_new_trends(self):
        """ Test when new trends are provided"""
        # Arrange
        trend = Trend(name="Test Trend", category="Test Category")
        new_trends = {trend: ["Post 1", "Post 2"]}

        # Act
        self.new_trends_sender.send(new_trends)

        # Assert
        expected_message = {
            'trend': "Test Trend",
            'category': "Test Category",
            'posts': ["Post 1", "Post 2"]
        }
        self.mock_sqs_adapter.send_message.assert_called_once_with(expected_message)

    def test_send_raises_exception(self):
        """ Test when sending a message raises an exception"""
        # Arrange
        trend = Trend(name="Test Trend", category="Test Category")
        new_trends = {trend: ["Post 1", "Post 2"]}
        self.mock_sqs_adapter.send_message.side_effect = Exception("SQS Error")

        # Act
        with self.assertRaises(Exception) as context:
            self.new_trends_sender.send(new_trends)

        # Assert
        self.assertEqual(str(context.exception), "SQS Error")
        self.mock_sqs_adapter.send_message.assert_called_once()


if __name__ == '__main__':
    unittest.main()

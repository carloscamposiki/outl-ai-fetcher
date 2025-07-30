import unittest
from unittest.mock import MagicMock, patch
from src.services.trends_fetcher import TrendsFetcher
from src.entity.trend import Trend


class TestTrendsFetcher(unittest.TestCase):

    def setUp(self):
        self.mock_dynamo_adapter = MagicMock()
        self.mock_blue_sky_api = MagicMock()
        self.trends_fetcher = TrendsFetcher(
            dynamo_adapter=self.mock_dynamo_adapter,
            blue_sky_api=self.mock_blue_sky_api,
            dynamo_table_name="test_table"
        )

    @patch('time.time', return_value=1234567890.0)
    def test_fetch_no_existing_trends(self, mock_time):
        """ Test when there are no existing trends in DynamoDB"""
        # Arrange
        self.mock_dynamo_adapter.get_item.return_value = {}
        self.mock_blue_sky_api.get_trends.return_value = [
            {'displayName': 'Trend 1', 'category': 'Category 1'},
            {'displayName': 'Trend 2', 'category': 'Category 2'}
        ]

        # Act
        result = self.trends_fetcher.fetch()

        # Assert
        expected_trends = [
            Trend(name='Trend 1', category='Category 1', created_at=1234567890.0),
            Trend(name='Trend 2', category='Category 2', created_at=1234567890.0)
        ]
        self.assertEqual(result, expected_trends)
        self.mock_dynamo_adapter.get_item.assert_called_once()
        self.mock_blue_sky_api.get_trends.assert_called_once()

    @patch('time.time', return_value=1234567890.0)
    def test_remove_expired_trends(self, mock_time):
        """ Test the removal of expired trends from existing trends"""
        # Arrange
        existing_trends = [
            Trend(name='Trend 1', category='Category 1', created_at=1234567890.0),
            Trend(name='Trend 2', category='Category 2', created_at=1234567890.0)
        ]

        # Act
        valid_trends = self.trends_fetcher._remove_expired_trends(existing_trends)

        # Assert
        self.assertEqual(valid_trends, [])
        self.mock_dynamo_adapter.put_item.assert_not_called()


if __name__ == '__main__':
    unittest.main()

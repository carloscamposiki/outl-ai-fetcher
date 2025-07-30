import unittest
from unittest.mock import MagicMock
from src.services.posts_fetcher import PostsFetcher
from src.entity.trend import Trend


class TestPostsFetcher(unittest.TestCase):

    def setUp(self):
        self.mock_blue_sky_api = MagicMock()
        self.posts_fetcher = PostsFetcher(blue_sky_api=self.mock_blue_sky_api)

    def test_fetch_no_trends(self):
        """ Test when no trends are provided, it should return an empty dictionary """
        # Arrange
        new_trends = []

        # Act
        result = self.posts_fetcher.fetch(new_trends)

        # Assert
        self.assertEqual(result, {})
        self.mock_blue_sky_api.search_posts.assert_not_called()

    def test_fetch_with_trends(self):
        """ Test when trends are provided, it should fetch posts for each trend """
        # Arrange
        trend1 = Trend(name="Trend 1", category="Category 1")
        trend2 = Trend(name="Trend 2", category="Category 2")
        new_trends = [trend1, trend2]

        self.mock_blue_sky_api.search_posts.side_effect = [
            ["Post 1", "Post 2"],
            ["Post A", "Post B"]
        ]

        # Act
        result = self.posts_fetcher.fetch(new_trends)

        # Assert
        expected_result = {
            trend1: ["Post 1", "Post 2"],
            trend2: ["Post A", "Post B"]
        }
        self.assertEqual(result, expected_result)
        self.mock_blue_sky_api.search_posts.assert_any_call("Trend 1")
        self.mock_blue_sky_api.search_posts.assert_any_call("Trend 2")

    def test_fetch_api_error(self):
        """ Test when the BlueSkyAPI raises an exception, it should propagate the exception """
        # Arrange
        trend = Trend(name="Trend 1", category="Category 1")
        new_trends = [trend]

        self.mock_blue_sky_api.search_posts.side_effect = Exception("API Error")

        # Act
        with self.assertRaises(Exception) as context:
            self.posts_fetcher.fetch(new_trends)

        # Assert
        self.assertEqual(str(context.exception), "API Error")
        self.mock_blue_sky_api.search_posts.assert_called_once_with("Trend 1")


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
from src.adapter.api.blue_sky_api import BlueSkyAPI
from src.exception.blue_sky_exception import BlueSkyException


class TestBlueSkyAPI(unittest.TestCase):

    def setUp(self):
        self.mock_token_manager = MagicMock()
        self.mock_session = MagicMock()
        self.mock_token_manager.get_session.return_value = self.mock_session
        self.mock_session.get_token.return_value = "mock_token"
        self.blue_sky_api = BlueSkyAPI(token_generator=self.mock_token_manager)

    @patch('src.adapter.api.blue_sky_api.requests.get')
    def test_get_trends_success(self, mock_get):
        """ Test when the get trends API returns a successful response """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'trends': [{'name': 'Trend 1'}, {'name': 'Trend 2'}]}
        mock_get.return_value = mock_response

        # Act
        result = self.blue_sky_api.get_trends()

        # Assert
        self.assertEqual(result, [{'name': 'Trend 1'}, {'name': 'Trend 2'}])
        mock_get.assert_called_once_with(
            'https://bsky.social/xrpc/app.bsky.unspecced.getTrends',
            headers={'Authorization': 'mock_token'}
        )

    @patch('src.adapter.api.blue_sky_api.requests.get')
    def test_get_trends_failure(self, mock_get):
        """ Test when the get trends API returns an error """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        # Act & Assert
        with self.assertRaises(BlueSkyException) as context:
            self.blue_sky_api.get_trends()

        self.assertEqual(
            str(context.exception),
            'Failed to fetch trends: 500 - Internal Server Error'
        )
        mock_get.assert_called_once()

    @patch('src.adapter.api.blue_sky_api.requests.get')
    def test_search_posts_success(self, mock_get):
        """ Test when the search posts API returns a successful response """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'posts': [{'record': {'text': 'Post 1'}}, {'record': {'text': 'Post 2'}}]
        }
        mock_get.return_value = mock_response

        # Act
        result = self.blue_sky_api.search_posts(query="test_query", limit=50)

        # Assert
        self.assertEqual(result, ['Post 1', 'Post 2'])
        mock_get.assert_called_once_with(
            'https://bsky.social/xrpc/app.bsky.feed.searchPosts?q=test_query&limit=50',
            headers={'Authorization': 'mock_token'}
        )

    @patch('src.adapter.api.blue_sky_api.requests.get')
    def test_search_posts_failure(self, mock_get):
        """ Test when the search posts API returns an error """
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # Act & Assert
        with self.assertRaises(BlueSkyException) as context:
            self.blue_sky_api.search_posts(query="test_query")

        self.assertEqual(
            str(context.exception),
            'Failed to search posts: 404 - Not Found'
        )
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()

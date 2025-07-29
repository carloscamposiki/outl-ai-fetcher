import requests
from src.exception.blue_sky_exception import BlueSkyException
from src.adapter.api.token_manager import TokenManager

class BlueSkyAPI:

    def __init__(self, token_generator: TokenManager):
        self.token_generator = token_generator

    def get_trends(self):
        url = 'https://bsky.social/xrpc/app.bsky.unspecced.getTrends'
        token = self.token_generator.get_session().get_token()
        headers = {'Authorization': token}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()['trends']
        else:
            raise BlueSkyException(f'Failed to fetch trends: {response.status_code} - {response.text}')

    def search_posts(self, query: str, limit: int = 100) -> list:
        url = f'https://bsky.social/xrpc/app.bsky.feed.searchPosts?q={query}&limit={limit}'
        token = self.token_generator.get_session().get_token()
        headers = {'Authorization': token}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return self.map_posts(response.json()['posts'])
        else:
            raise BlueSkyException(f'Failed to search posts: {response.status_code} - {response.text}')

    def map_posts(self, response: map) -> list[str]:
        posts = []
        for item in response:
            posts.append(item['record']['text'])
        return posts

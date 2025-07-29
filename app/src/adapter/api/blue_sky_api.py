import requests
from src.exception.blue_sky_exception import BlueSkyException
from src.entity.post import Post
from src.adapter.api.token_generator import TokenGenerator

class BlueSkyAPI:

    def __init__(self, token_generator: TokenGenerator):
        self.token_generator = token_generator
        self.base_url = 'https://api.bsky.app/v1'

    def get_user_posts(self, username: str, limit: int = 100) -> list[Post]:
        url = f'https://bsky.social/xrpc/app.bsky.feed.getAuthorFeed?actor={username}&limit={limit}'
        headers = {'Authorization': self.token_generator.get_token()}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return self.map_posts(response.json()['feed'])
        else:
            raise BlueSkyException(f'Failed to fetch posts: {response.status_code} - {response.text}')

    def get_trends(self):
        url = 'https://bsky.social/xrpc/app.bsky.unspecced.getTrends'
        headers = {'Authorization': self.token_generator.get_token()}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()['trends']
        else:
            raise BlueSkyException(f'Failed to fetch trends: {response.status_code} - {response.text}')

    def search_posts(self, query: str, limit: int = 100) -> list:
        url = f'{self.base_url}/search?query={query}&limit={limit}'
        headers = {'Authorization': f'Bearer {self.api_key}'}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return self.map_posts(response.json()['posts'])
        else:
            raise BlueSkyException(f'Failed to search posts: {response.status_code} - {response.text}')

    def map_posts(self, response: map) -> list[Post]:
        posts = []
        for item in response:
            post = Post(
                cid=item['post']['cid'],
                content=item['post']['record']['text']
            )
            posts.append(post)
        return posts

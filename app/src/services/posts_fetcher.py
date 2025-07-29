from src.adapter.api.blue_sky_api import BlueSkyAPI
from src.entity.trend import Trend


class PostsFetcher:
    def __init__(self,
                 blue_sky_api: BlueSkyAPI):
        self.blue_sky_api = blue_sky_api

    def fetch(self, new_trends: list[Trend]) -> dict[Trend, list[str]]:
        posts_content = {}
        for trend in new_trends:
            posts = self.blue_sky_api.search_posts(trend.name)
            posts_content[trend] = posts
        return posts_content

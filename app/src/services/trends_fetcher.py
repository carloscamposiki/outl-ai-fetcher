from src.entity.trend import Trend
from src.adapter.aws.dynamo import DynamoAdapter
from src.adapter.api.blue_sky_api import BlueSkyAPI
import re
import time

class TrendsFetcher:

    def __init__(self,
                 dynamo_adapter: DynamoAdapter,
                 blue_sky_api: BlueSkyAPI,
                 dynamo_table_name: str
                 ):
        self.dynamo_adapter = dynamo_adapter
        self.dynamo_table_name = dynamo_table_name
        self.blue_sky_api = blue_sky_api

    def fetch(self) -> list[Trend]:
        existing_trends = self._get_existing_trends()
        new_trends = self._get_new_trends(existing_trends)
        self._update_existing_trends(new_trends=new_trends,
                                     existing_trends=existing_trends)
        return new_trends

    def _get_new_trends(self, existing_trends: list[Trend]) -> list[Trend]:
        latest_trends = []
        trends_response = self.blue_sky_api.get_trends()
        if not trends_response:
            raise ValueError('No trends found in the response.')
        for trend in trends_response:
            new_trend = Trend(
                name=trend['name'],
                category=trend.get('category', 'general')
            )
            latest_trends.append(new_trend)
        existing_trends_name = [trend.name for trend in existing_trends]
        new_trends = []
        for trend in latest_trends:
            if trend.name not in existing_trends_name:
                new_trends.append(trend)
        return new_trends

    def _update_existing_trends(self, new_trends: list[Trend], existing_trends: list[Trend]) -> None:
        valid_trends = self._remove_expired_trends(existing_trends)
        valid_trends.extend(new_trends)
        self._save_updated_trends_dynamo(valid_trends)

    def _get_existing_trends(self) -> list[Trend]:
        item = self.dynamo_adapter.get_item(
            table_name=self.dynamo_table_name,
            key={
                'type': 'cache',
                'id': 'trends'
            }
        )
        if not item or 'trends' not in item:
            return []
        trends = []
        for trend_dict in item.get('trends'):
            trend = Trend(
                name=trend_dict['name'],
                category=trend_dict['category'],
                created_at=trend_dict['created_at']
            )
            trends.append(trend)
        return trends

    def _save_updated_trends_dynamo(self, trends: list[Trend]) -> None:
        item = {
            'type': 'cache',
            'id': 'trends',
            'trends': [
                {'name': trend.name, 'created_at': trend.created_at} for trend in trends
            ]
        }
        self.dynamo_adapter.put_item(
            table_name=self.dynamo_table_name,
            item=item
        )

    def _extract_trends_from_post(self, text: str) -> list[str]:
        trends = re.findall(r'#\w+', text)
        if not trends:
            raise ValueError('No trends found in the post content.')
        return trends

    def _remove_expired_trends(self, existing_trends: list[Trend]) -> list[Trend]:
        valid_trends = []
        for trend in existing_trends:
            if trend.created_at < time.time() - 24 * 60 * 60:
                valid_trends.append(trend)
        return valid_trends

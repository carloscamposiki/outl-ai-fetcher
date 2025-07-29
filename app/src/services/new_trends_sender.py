from src.adapter.aws.sqs import SqsAdapter
from src.entity.trend import Trend

class NewTrendsSender:

    def __init__(self,
                 sqs_adapter: SqsAdapter):
        self.sqs_adapter = sqs_adapter

    def send(self, new_trends: dict[Trend, list[str]]) -> None:
        if not new_trends:
            print('No new trends to send.')
            return

        for (trend, posts) in new_trends.items():
            message = {
                'trend': trend.name,
                'category': trend.category,
                'posts': posts
            }
            try:
                self.sqs_adapter.send_message(message)
            except Exception as e:
                print(f'Failed to send message for trend {trend.name}: {e}')
                raise

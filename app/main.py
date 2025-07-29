from src.adapter.api.blue_sky_api import BlueSkyAPI
from src.adapter.api.token_generator import TokenGenerator
from src.adapter.aws.secrets_manager import SecretsManager
from src.adapter.aws.dynamo import DynamoAdapter
from src.adapter.aws.sqs import SqsAdapter
from src.services.trends_fetcher import TrendsFetcher
from src.services.posts_fetcher import PostsFetcher
from src.services.new_trends_sender import NewTrendsSender
import os

token_secret_name = os.getenv('TOKEN_SECRET_NAME')
blue_sky_credentials_secret_name = os.getenv('BLUE_SKY_CREDENTIALS_SECRET_NAME')
trends_processing_queue = os.getenv('TRENDS_PROCESSING_QUEUE')
dynamo_table_name = os.getenv('DYNAMO_TABLE_NAME')

secrets_manager = SecretsManager()
dynamo_adapter = DynamoAdapter()
sqs_adapter = SqsAdapter(trends_processing_queue)

token_generator = TokenGenerator(secrets_manager=secrets_manager,
                                 token_secret_name=token_secret_name,
                                 blue_sky_credentials_secret_name=blue_sky_credentials_secret_name)

blue_sky_api = BlueSkyAPI(token_generator)

trend_fetcher = TrendsFetcher(dynamo_adapter=dynamo_adapter,
                              blue_sky_api=blue_sky_api,
                              dynamo_table_name='trends_cache')
posts_fetcher = PostsFetcher(blue_sky_api)
new_trends_sender = NewTrendsSender(sqs_adapter)


def handler(_, __):
    trends = trend_fetcher.fetch()
    new_trends = posts_fetcher.fetch(trends)
    new_trends_sender.send(new_trends)

    return {
        'statusCode': 200
    }

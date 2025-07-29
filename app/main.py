from src.adapter.api.blue_sky_api import BlueSkyAPI
from src.adapter.api.token_manager import TokenManager
from src.adapter.aws.secrets_manager import SecretsManager
from src.adapter.aws.dynamo import DynamoAdapter
from src.adapter.aws.sqs import SqsAdapter
from src.services.trends_fetcher import TrendsFetcher
from src.services.posts_fetcher import PostsFetcher
from src.services.new_trends_sender import NewTrendsSender
import os

session_secret_name = os.getenv('SESSION_SECRET_NAME')
blue_sky_credentials_secret_name = os.getenv('BLUE_SKY_CREDENTIALS_SECRET_NAME')
trends_processing_queue = os.getenv('TRENDS_PROCESSING_QUEUE')
dynamo_table_name = os.getenv('DYNAMO_TRENDS_TABLE_NAME')

secrets_manager = SecretsManager()
dynamo_adapter = DynamoAdapter()
sqs_adapter = SqsAdapter(trends_processing_queue)

token_manager = TokenManager(secrets_manager=secrets_manager,
                               session_secret_name=session_secret_name,
                               blue_sky_credentials_secret_name=blue_sky_credentials_secret_name)

blue_sky_api = BlueSkyAPI(token_manager)

trends_fetcher = TrendsFetcher(dynamo_adapter=dynamo_adapter,
                               blue_sky_api=blue_sky_api,
                               dynamo_table_name=dynamo_table_name)
posts_fetcher = PostsFetcher(blue_sky_api)
new_trends_sender = NewTrendsSender(sqs_adapter)


def lambda_handler(_, __):
    trends = trends_fetcher.fetch()
    new_trends = posts_fetcher.fetch(trends)
    new_trends_sender.send(new_trends)

    return {
        'statusCode': 200
    }

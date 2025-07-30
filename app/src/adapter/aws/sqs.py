import boto3
import json

class SqsAdapter:

    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        self.client = boto3.client('sqs')

    def send_message(self, message: dict) -> None:
        try:
            response = self.client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message, ensure_ascii=False)
            )
        except Exception as e:
            print(f'Error sending message: {e}')
            raise

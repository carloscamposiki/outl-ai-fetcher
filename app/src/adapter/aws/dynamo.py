import boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer

class DynamoAdapter:

    def __init__(self):
        self.client = boto3.client('dynamodb', region_name='us-east-1')
        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    def put_item(self, table_name: str, item: dict) -> None:
        try:
            # Serialize the item to DynamoDB format
            serialized_item = {k: self.serializer.serialize(v) for k, v in item.items()}
            self.client.put_item(
                TableName=table_name,
                Item=serialized_item
            )
            print(f"Item added to table {table_name} successfully.")
        except Exception as e:
            print(f"Error adding item to table {table_name}: {e}")
            raise

    def get_item(self, table_name: str, key: dict) -> dict:
        try:
            # Serialize the key to DynamoDB format
            serialized_key = {k: self.serializer.serialize(v) for k, v in key.items()}
            response = self.client.get_item(
                TableName=table_name,
                Key=serialized_key
            )
            # Deserialize the item back to Python format
            return {k: self.deserializer.deserialize(v) for k, v in response.get('Item', {}).items()}
        except Exception as e:
            print(f"Error retrieving item from table {table_name}: {e}")
            raise
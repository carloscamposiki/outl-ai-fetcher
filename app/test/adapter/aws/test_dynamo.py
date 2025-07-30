import unittest
from unittest.mock import MagicMock, patch
from src.adapter.aws.dynamo import DynamoAdapter


class TestDynamoAdapter(unittest.TestCase):

    def setUp(self):
        self.mock_boto3_client = MagicMock()
        self.mock_type_serializer = MagicMock()
        self.mock_type_deserializer = MagicMock()

        with patch('boto3.client', return_value=self.mock_boto3_client):
            self.dynamo_adapter = DynamoAdapter()

        self.dynamo_adapter.serializer = self.mock_type_serializer
        self.dynamo_adapter.deserializer = self.mock_type_deserializer

    def test_put_item_success(self):
        """ Test when the put item API returns a successful response """
        # Arrange
        table_name = "test_table"
        item = {"id": "123", "name": "Test Item"}
        serialized_item = {"id": {"S": "123"}, "name": {"S": "Test Item"}}
        self.mock_type_serializer.serialize.side_effect = lambda x: {"S": x}

        # Act
        self.dynamo_adapter.put_item(table_name, item)

        # Assert
        self.mock_boto3_client.put_item.assert_called_once_with(
            TableName=table_name,
            Item=serialized_item
        )

    def test_put_item_failure(self):
        """ Test when the put item API returns an error """
        # Arrange
        table_name = "test_table"
        item = {"id": "123", "name": "Test Item"}
        self.mock_boto3_client.put_item.side_effect = Exception("DynamoDB Error")

        # Act
        with self.assertRaises(Exception) as context:
            self.dynamo_adapter.put_item(table_name, item)

        # Assert
        self.assertEqual(str(context.exception), "DynamoDB Error")

    def test_get_item_success(self):
        """ Test when the get item API returns a successful response """
        # Arrange
        table_name = "test_table"
        key = {"id": "123"}
        serialized_key = {"id": {"S": "123"}}
        dynamo_response = {"Item": {"id": {"S": "123"}, "name": {"S": "Test Item"}}}
        deserialized_item = {"id": "123", "name": "Test Item"}

        self.mock_type_serializer.serialize.side_effect = lambda x: {"S": x}
        self.mock_type_deserializer.deserialize.side_effect = lambda x: x["S"]
        self.mock_boto3_client.get_item.return_value = dynamo_response

        # Act
        result = self.dynamo_adapter.get_item(table_name, key)

        # Assert
        self.assertEqual(result, deserialized_item)
        self.mock_boto3_client.get_item.assert_called_once_with(
            TableName=table_name,
            Key=serialized_key
        )

    def test_get_item_not_found(self):
        """ Test when the get item API returns no item found """
        # Arrange
        table_name = "test_table"
        key = {"id": "123"}
        self.mock_boto3_client.get_item.return_value = {}  # Return an empty dictionary

        # Act
        result = self.dynamo_adapter.get_item(table_name, key)

        # Assert
        self.assertIsNone(result)
        self.mock_boto3_client.get_item.assert_called_once()

    def test_get_item_failure(self):
        """ Test when the get item API returns an error """
        # Arrange
        table_name = "test_table"
        key = {"id": "123"}
        self.mock_boto3_client.get_item.side_effect = Exception("DynamoDB Error")

        # Act
        with self.assertRaises(Exception) as context:
            self.dynamo_adapter.get_item(table_name, key)

        # Assert
        self.assertEqual(str(context.exception), "DynamoDB Error")


if __name__ == '__main__':
    unittest.main()

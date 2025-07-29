import boto3
import json

class SecretsManager:

    def __init__(self, region_name: str):
        self.client = boto3.client('secretsmanager', region_name=region_name)

    def get_secret(self, secret_name: str) -> dict:
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            else:
                raise ValueError("Secret is not in string format.")
        except Exception as e:
            print(f"Error retrieving secret: {e}")
            raise

    def update_secret(self, secret_name: str, new_secret_value: dict) -> None:
        try:
            self.client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(new_secret_value)
            )
            print(f"Secret '{secret_name}' updated successfully.")
        except Exception as e:
            print(f"Error updating secret: {e}")
            raise

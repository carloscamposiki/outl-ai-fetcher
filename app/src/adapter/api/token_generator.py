from src.adapter.aws.secrets_manager import SecretsManager
from time import time
import requests

from src.entity.token import Token
from src.exception.blue_sky_exception import BlueSkyException


def _to_token(secret_data: dict) -> Token:
    token = secret_data.get('token')
    refresh_token = secret_data.get('refresh_token')
    token_generated_at = secret_data.get('token_generated_at')
    refresh_token_generated_at = secret_data.get('refresh_token_generated_at')
    return Token(
        token=token,
        refresh_token=refresh_token,
        token_generated_at=token_generated_at,
        refresh_token_generated_at=refresh_token_generated_at
    )

class TokenGenerator:

    def __init__(self,
                 secrets_manager: SecretsManager,
                 token_secret_name: str,
                 blue_sky_credentials_secret_name: str):
        self.secrets_manager = secrets_manager
        self.token_secret_name = token_secret_name
        self.token = self._retrieve_token()
        self.blue_sky_credentials_secret_name = blue_sky_credentials_secret_name

    def _retrieve_token(self) -> Token:
        token_json = self.secrets_manager.get_secret(self.token_secret_name)
        return _to_token(token_json)

    def get_token(self) -> Token:
        if self.token.is_token_expired():
            self._generate_token()
        return self.token

    def _generate_token(self) -> Token:
        if self.token.is_refresh_token_expired():
            self._generate_new_token()
        else:
            self._refresh_token()

    def _generate_new_token(self) -> None:
        credentials = self._get_user_credentials()
        self.token = self.blueSkyApi.generate_token(
            username=credentials['username'],
            password=credentials['password']
        )
        self._update_secrets_manager()

    def _refresh_token(self) -> None:
        token_data = self.blueSkyApi.refresh_token(self.token.refresh_token)
        new_token = Token(
            token=f"Bearer {token_data['token']}",
            refresh_token=f"Bearer {token_data['refresh_token']}",
            token_generated_at=time(),
            refresh_token_generated_at=self.token.refresh_token_generated_at
        )
        self.token = new_token
        self._update_secrets_manager()

    def _get_user_credentials(self) -> dict:
        return self.secrets_manager.get_secret(self.blue_sky_credentials_secret_name)

    def _update_secrets_manager(self) -> None:
        return self.secrets_manager.update_secret(
            secret_name=self.token_secret_name,
            new_secret_value={
                'token': self.token.token,
                'refresh_token': self.token.refresh_token,
                'token_generated_at': self.token.token_generated_at,
                'refresh_token_generated_at': self.token.refresh_token_generated_at
            }
        )

    def generate_token(self, username: str, password: str) -> dict:
        url = f'{self.base_url}/auth/login'
        payload = {
            'identifier': username,
            'password': password
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return {
                'token': f"Bearer{response.json().get('accessJwt')}",
                'refresh_token': f"Bearer{response.json().get('refreshJwt')}"
            }
        else:
            raise BlueSkyException(f'Failed to generate token: {response.status_code} - {response.text}')

    def refresh_token(self, refresh_token: str) -> dict:
        url = f'{self.base_url}/auth/refresh'
        payload = {
            'refresh_token': refresh_token
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return {
                'token': f"Bearer{response.json().get('accessJwt')}",
                'refresh_token': f"Bearer{response.json().get('refreshJwt')}"
            }
        else:
            raise BlueSkyException(f'Failed to refresh token: {response.status_code} - {response.text}')

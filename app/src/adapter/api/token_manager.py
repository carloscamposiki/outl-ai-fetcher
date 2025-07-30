from src.adapter.aws.secrets_manager import SecretsManager
from time import time
import requests

from src.entity.session import Session
from src.exception.blue_sky_exception import BlueSkyException

class TokenManager:

    def __init__(self,
                 secrets_manager: SecretsManager,
                 session_secret_name: str,
                 blue_sky_credentials_secret_name: str):
        self.secrets_manager = secrets_manager
        self.session_secret_name = session_secret_name
        self.session = self._retrieve_session()
        self.blue_sky_credentials_secret_name = blue_sky_credentials_secret_name

    def _retrieve_session(self) -> Session:
        session_secret = self.secrets_manager.get_secret(self.session_secret_name)
        return self._to_session(session_secret)

    def get_session(self) -> Session:
        if self.session.is_token_expired():
            print("Token expired")
            self._generate_session()
        return self.session

    def _generate_session(self) -> None:
        if self.session.is_refresh_token_expired():
            print("Refresh token expired")
            self._generate_new_session()
        else:
            try:
                self._refresh_session()
            except BlueSkyException as e:
                print(f"Failed to refresh session: {e}")
                self._generate_new_session()

    def _generate_new_session(self) -> None:
        user_credentials = self._get_user_credentials()
        self.session = self._generate_token(
            username=user_credentials['username'],
            password=user_credentials['password']
        )
        self._update_secrets_manager()

    def _refresh_session(self) -> None:
        print("Refreshing session " + self.session.refresh_token)
        session_data = self._refresh_token(self.session.refresh_token)
        new_session = Session(
            token=f'Bearer {session_data["token"]}',
            refresh_token=f'Bearer {session_data["refresh_token"]}',
            token_generated_at=time(),
            refresh_token_generated_at=self.session.refresh_token_generated_at
        )
        self.session = new_session
        self._update_secrets_manager()

    def _get_user_credentials(self) -> dict:
        return self.secrets_manager.get_secret(self.blue_sky_credentials_secret_name)

    def _update_secrets_manager(self) -> None:
        new_secret_value = {
            'token': self.session.token,
            'refresh_token': self.session.refresh_token,
            'token_generated_at': self.session.token_generated_at,
            'refresh_token_generated_at': self.session.refresh_token_generated_at
        }
        self.secrets_manager.update_secret(
            secret_name=self.session_secret_name,
            new_secret_value=new_secret_value
        )

    def _generate_token(self, username: str, password: str) -> Session:
        url = 'https://bsky.social/xrpc/com.atproto.server.createSession'
        payload = {
            'identifier': username,
            'password': password
        }
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return Session(
                token=f'Bearer {response.json().get("accessJwt")}',
                refresh_token=f'Bearer {response.json().get("refreshJwt")}'
            )
        else:
            raise BlueSkyException(f'Failed to generate token: {response.status_code} - {response.text}')

    def _refresh_token(self, refresh_token: str) -> dict:
        url = 'https://bsky.social/xrpc/com.atproto.server.refreshSession'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': refresh_token
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return {
                'token': f'Bearer{response.json().get("accessJwt")}',
                'refresh_token': f'Bearer{response.json().get("refreshJwt")}'
            }
        elif response.status_code == 400:
            raise BlueSkyException('Invalid refresh token')
        else:
            raise BlueSkyException(f'Failed to refresh token: {response.status_code} - {response.text}')

    def _to_session(self, session_secret: dict) -> Session:
        token = session_secret.get('token')
        refresh_token = session_secret.get('refresh_token')
        token_generated_at = session_secret.get('token_generated_at')
        refresh_token_generated_at = session_secret.get('refresh_token_generated_at')
        return Session(
            token=token,
            refresh_token=refresh_token,
            token_generated_at=token_generated_at,
            refresh_token_generated_at=refresh_token_generated_at
        )

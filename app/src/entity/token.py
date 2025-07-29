from time import time
import json

class Token:

    @classmethod
    def from_blue_sky_reponse(cls, response_json: str) -> 'Token':
        response = json.loads(response_json)
        return Token(
            token=response.get('accessJwt'),
            refresh_token=response.get('refreshJwt')
        )

    def __init__(self,
                 token: str,
                 refresh_token: str,
                 token_generated_at: float = None,
                 refresh_token_generated_at: float = None
                 ):
        self.token = token
        self.refresh_token = refresh_token
        self.token_generated_at = token_generated_at or time()
        self.refresh_token_generated_at = refresh_token_generated_at or time()

    def is_token_expired(self, expiration_time: int = 90 * 60) -> bool:
        return (time() - self.token_generated_at) > expiration_time

    def is_refresh_token_expired(self, expiration_time: int = 58 * 24 * 60 * 60) -> bool:
        return (time() - self.refresh_token_generated_at) > expiration_time

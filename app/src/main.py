from src.adapter.api.blue_sky_api import BlueSkyAPI

def handler(event, context):
    """
    Lambda function handler to generate a new token for BlueSky API.

    :param event: The event data passed to the Lambda function.
    :param context: The runtime information of the Lambda function.
    :return: A dictionary containing the new token and refresh token.
    """
    blue_sky_api = BlueSkyAPI()
    token = blue_sky_api.generate_token()
    print(token)
    return {
        'statusCode': 200,
        'body': {
            'token': token.token,
            'refresh_token': token.refresh_token
        }
    }
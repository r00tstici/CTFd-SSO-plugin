from CTFd.utils import get_app_config


def register_client(oauth):
    oauth.register(
        name='client',
        client_id=get_app_config('OAUTH_CLIENT_ID'),
        client_secret=get_app_config('OAUTH_CLIENT_SECRET'),
        access_token_url=get_app_config('OAUTH_TOKEN_ENDPOINT'),
        authorize_url=get_app_config('OAUTH_AUTHORIZATION_ENDPOINT'),
        client_kwargs={'scope': 'profile roles'},
    )

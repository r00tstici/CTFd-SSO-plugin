from CTFd.models import db
from CTFd.utils import get_app_config


class OAuthClients(db.Model):
    __tablename__ = "oauth_clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    client_id = db.Column(db.Text)
    client_secret = db.Column(db.Text)
    access_token_url = db.Column(db.Text)
    authorize_url = db.Column(db.Text)
    api_base_url = db.Column(db.Text)
    admin_role = db.Column(db.Text)
    user_role = db.Column(db.Text)

    # In a later update you will be able to customize the login button 
    color = db.Column(db.Text)
    icon = db.Column(db.Text)

    def register(self, oauth):
        if get_app_config("OAUTH_ALL_SCOPES") is not None and len(str(get_app_config("OAUTH_ALL_SCOPES")).replace('\"', '')) > 0:
            local_client_kwargs={'scope': str(get_app_config("OAUTH_ALL_SCOPES")).replace('\"', '')}
        else:
            local_client_kwargs={'scope': 'profile roles'}
        oauth.register(
            name=self.id,
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token_url=self.access_token_url,
            authorize_url=self.authorize_url,
            api_base_url=self.api_base_url,
            admin_role=self.admin_role,
            user_role=self.user_role,
            client_kwargs=local_client_kwargs
            
        )

    def disconnect(self, oauth):
        oauth._registry[self.id] = None
        oauth._clients[self.id] = None

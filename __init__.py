""" Plugin entry-point """

import json
import os
import re

from authlib.integrations.flask_client import OAuth

from CTFd.plugins import override_template
from CTFd.utils import get_app_config

from .blueprint import load_bp
from .models import OAuthClients

PLUGIN_PATH = os.path.dirname(__file__)
CONFIG = json.load(open("{}/config.json".format(PLUGIN_PATH)))


def oauth_clients():
    return OAuthClients.query.all()


def update_login_template(app):
    """
    Gets the actual login template and injects 
    the SSO buttons before the Forms.auth.LoginForm block
    """

    environment = app.jinja_environment
    original = app.theme_loader.get_source(environment, 'login.html')[0]

    match = re.search(".*Forms\.auth\.LoginForm.*\n", original)

    # If Forms.auth.LoginForm is not found (maybe in a custom template), it does nothing
    if match:
        pos = match.start()

        PLUGIN_PATH = os.path.dirname(__file__)
        injecting_file_path = os.path.join(
            PLUGIN_PATH, 'templates/login_oauth.html')
        with open(injecting_file_path, 'r') as f:
            injecting = f.read()

        new_template = original[:pos] + injecting + original[pos:]
        override_template('login.html', new_template)


def load(app):
    # Create database tables
    app.db.create_all()

    # Get all saved clients and register them
    clients = oauth_clients()
    oauth = OAuth(app)
    for client in clients:
        client.register(oauth)

    # Register oauth_clients() as template global
    app.jinja_env.globals.update(oauth_clients=oauth_clients)

    # Update the login template
    if get_app_config("OAUTH_CREATE_BUTTONS") == True:
        update_login_template(app)

    # Register the blueprint containing the routes
    bp = load_bp(oauth)
    app.register_blueprint(bp)

from flask import Blueprint, redirect, url_for, session, request

from CTFd.models import Users, db
from CTFd.utils import get_app_config, get_config
from CTFd.cache import clear_user_session
from CTFd.utils.config.visibility import registration_visible
from CTFd.utils.security.auth import login_user
from CTFd.utils.helpers import error_for
from CTFd.utils.logging import log
from CTFd.utils.modes import TEAMS_MODE

import requests

plugin_bp = Blueprint('sso', __name__, template_folder='templates')

def load_bp(app):

    @plugin_bp.route("/sso/login", methods = ['GET'])
    def sso_oauth():
        endpoint = get_app_config('OAUTH_AUTHORIZATION_ENDPOINT')
        redirect_uri = url_for('.sso_redirect', _external = True)
        client_id = get_app_config('OAUTH_CLIENT_ID')
        scope = 'profile roles'

        if client_id is None or endpoint is None:
            error_for(
                endpoint="auth.login",
                message="OAuth Settings not configured. "
                "Ask your CTF administrator to configure SSO integration.",
            )
            return redirect(url_for("auth.login"))

        redirect_url = "{endpoint}?redirect_uri={redirect_uri}&response_type=code&client_id={client_id}&scope={scope}&state={state}".format(
            redirect_uri=redirect_uri, endpoint=endpoint, client_id=client_id, scope=scope, state=session["nonce"]
        )

        return redirect(redirect_url)

    @plugin_bp.route("/sso/redirect", methods = ['GET'])
    def sso_redirect():
        oauth_code = request.args.get("code")

        state = request.args.get("state")

        if session["nonce"] != state:
            log("logins", "[{date}] {ip} - OAuth State validation mismatch")
            error_for(endpoint="auth.login", message="OAuth State validation mismatch.")
            return redirect(url_for("auth.login"))

        if oauth_code:
            url = get_app_config("OAUTH_TOKEN_ENDPOINT")

            client_id = get_app_config("OAUTH_CLIENT_ID")
            client_secret = get_app_config("OAUTH_CLIENT_SECRET")

            headers = {"Content-type": "application/x-www-form-urlencoded"}
            data = {
                "code": oauth_code,
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "authorization_code",
                'redirect_uri' : url_for('.sso_redirect', _external = True),
            }
            token_request = requests.post(url, data=data, headers=headers)

            if token_request.status_code == requests.codes.ok:
                token = token_request.json()["access_token"]
                user_url = get_app_config("OAUTH_API_ENDPOINT")

                headers = {
                    "Authorization": "Bearer " + str(token),
                    "Content-type": "application/json",
                }
                api_data = requests.get(url=user_url, headers=headers).json()

                user_name = api_data["preferred_username"]
                user_email = api_data["email"]
                user_roles = api_data.get("roles")

                user = Users.query.filter_by(email=user_email).first()
                if user is None:
                    # Check if we are allowing registration before creating users
                    if registration_visible():
                        user = Users(
                            name=user_name,
                            email=user_email,
                            verified=True,
                        )
                        db.session.add(user)
                        db.session.commit()
                    else:
                        log("logins", "[{date}] {ip} - Public registration via MLC blocked")
                        error_for(
                            endpoint="auth.login",
                            message="Public registration is disabled. Please try again later.",
                        )
                        return redirect(url_for("auth.login"))

                user.verified = True
                db.session.commit()

                user_role = user_roles[0] if user_roles is not None and len(user_roles) > 0 and user_roles[0] in ["admin"] else "user"
                print(user_role)
                if user_role != user.type:
                    user.type = user_role
                    db.session.commit()
                    user = Users.query.filter_by(email=user_email).first()
                    clear_user_session(user_id=user.id)

                login_user(user)

                return redirect(url_for("challenges.listing"))
            else:
                log("logins", "[{date}] {ip} - OAuth token retrieval failure")
                error_for(endpoint="auth.login", message="OAuth token retrieval failure.")
                return redirect(url_for("auth.login"))
        else:
            log("logins", "[{date}] {ip} - Received redirect without OAuth code")
            error_for(
                endpoint="auth.login", message="Received redirect without OAuth code."
            )
            return redirect(url_for("auth.login"))

    return plugin_bp

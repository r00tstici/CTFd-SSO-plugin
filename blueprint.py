from flask import Blueprint, redirect, url_for, session, request

from CTFd.models import Users, db
from CTFd.utils import get_app_config
from CTFd.cache import clear_user_session
from CTFd.utils.config.visibility import registration_visible
from CTFd.utils.security.auth import login_user
from CTFd.utils.helpers import error_for
from CTFd.utils.logging import log

plugin_bp = Blueprint('sso', __name__, template_folder='templates')


def load_bp(app, oauth):

    @plugin_bp.route("/sso/login", methods = ['GET'])
    def sso_oauth():
        redirect_uri=url_for('.sso_redirect', _external=True)
        return oauth.client.authorize_redirect(redirect_uri)

    @plugin_bp.route("/sso/redirect", methods = ['GET'])
    def sso_redirect():
        oauth.client.authorize_access_token()
        userinfo_endpoint = get_app_config("OAUTH_API_ENDPOINT")
        api_data = oauth.client.get(userinfo_endpoint).json()

        user_name = api_data["preferred_username"]
        user_email = api_data["email"]
        user_roles = api_data.get("roles")

        user = Users.query.filter_by(email=user_email).first()
        if user is None:
            # Check if we are allowing registration before creating users
            if registration_visible() or get_app_config("OAUTH_ALWAYS_POSSIBLE") == True:
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

        if user_roles is not None and len(user_roles) > 0 and user_roles[0] in ["admin", "user"]:
            user_role = user_roles[0]
            if user_role != user.type:
                user.type = user_role
                db.session.commit()
                user = Users.query.filter_by(email=user_email).first()
                clear_user_session(user_id=user.id)

        login_user(user)

        return redirect(url_for("challenges.listing"))

    return plugin_bp

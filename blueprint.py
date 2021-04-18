from flask import Blueprint, redirect, url_for, session
from .controllers import ConfigController

from CTFd.models import Users, db
from CTFd.utils.security.auth import login_user
from CTFd.utils.logging import log

plugin_bp = Blueprint('sso', __name__, template_folder='templates')

def load_bp(oidc):
    @plugin_bp.route('/sso/login', methods = ['GET'])
    @oidc.require_login
    def oidc_login():
        info = oidc.user_getinfo(['email'])
        email = info.get('email')

        user = Users.query.filter_by(email=email).first()

        if user:
            session.regenerate()

            login_user(user)
            log("logins", "[{date}] {ip} - {name} logged in", name=user.name)

            db.session.close()

        return redirect(url_for("challenges.listing"))

    return plugin_bp

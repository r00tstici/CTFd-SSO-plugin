from flask import Blueprint, redirect, render_template, request, url_for
from wtforms import StringField
from wtforms.validators import InputRequired

from CTFd.cache import clear_user_session
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import Users, db
from CTFd.utils import get_app_config
from CTFd.utils.config.visibility import registration_visible
from CTFd.utils.decorators import admins_only
from CTFd.utils.helpers import error_for
from CTFd.utils.logging import log
from CTFd.utils.security.auth import login_user

from .models import OAuthClients

plugin_bp = Blueprint('sso', __name__, template_folder='templates', static_folder='static', static_url_path='/static/sso')


class OAuthForm(BaseForm):
    name = StringField("Client name", validators=[InputRequired()])
    client_id = StringField("OAuth client id", validators=[InputRequired()])
    client_secret = StringField("OAuth client secret", validators=[InputRequired()])
    access_token_url = StringField("Access token url", validators=[InputRequired()])
    authorize_url = StringField("Authorization url", validators=[InputRequired()])
    api_base_url = StringField("User info url", validators=[InputRequired()])
    admin_role = StringField("Admin SSO role", validators=[InputRequired()])
    user_role = StringField("User SSO role", validators=[InputRequired()])
    submit = SubmitField("Add")


def load_bp(oauth):

    @plugin_bp.route('/admin/sso')
    @admins_only
    def sso_list():
        return render_template('list.html')


    @plugin_bp.route('/admin/sso/client/<int:client_id>', methods = ['GET', 'DELETE'])
    @admins_only
    def sso_details(client_id):
        if request.method == 'DELETE':
            client = OAuthClients.query.filter_by(id=client_id).first()
            if client:
                client.disconnect(oauth)
                db.session.delete(client)
                db.session.commit()
                db.session.flush()
        return redirect(url_for('sso.sso_list'))


    @plugin_bp.route('/admin/sso/create', methods = ['GET', 'POST'])
    @admins_only
    def sso_create():
        if request.method == "POST":
            name = request.form["name"]
            client_id = request.form["client_id"]
            client_secret = request.form["client_secret"]
            access_token_url = request.form["access_token_url"]
            authorize_url = request.form["authorize_url"]
            api_base_url = request.form["api_base_url"]
            admin_role = request.form["admin_role"]
            user_role = request.form["user_role"]

            client = OAuthClients(
                name=name,
                client_id=client_id,
                client_secret=client_secret,
                access_token_url=access_token_url,
                authorize_url=authorize_url,
                api_base_url=api_base_url,
                admin_role=admin_role,
                user_role=user_role
            )
            db.session.add(client)
            db.session.commit()
            db.session.flush()

            client.register(oauth)

            return redirect(url_for('sso.sso_list'))

        form = OAuthForm()
        return render_template('create.html', form=form)


    @plugin_bp.route("/sso/login/<int:client_id>", methods = ['GET'])
    def sso_oauth(client_id):
        client = oauth.create_client(client_id)
        redirect_uri=url_for('sso.sso_redirect', client_id=client_id, _external=True)
        return client.authorize_redirect(redirect_uri)


    @plugin_bp.route("/sso/redirect/<int:client_id>", methods = ['GET'])
    def sso_redirect(client_id):
        client = oauth.create_client(client_id)
        client.authorize_access_token()
        api_data = client.get('').json()

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

        if user_roles is not None and len(user_roles) > 0 and user_roles[0] in [OAuthClients.query.filter_by(client_id=client_id).first().admin_role, OAuthClients.query.filter_by(client_id=client_id).first().user_role]:
            user_role = user_roles[0]
            if user_role != user.type:
                user.type = user_role
                db.session.commit()
                user = Users.query.filter_by(email=user_email).first()
                clear_user_session(user_id=user.id)

        login_user(user)

        return redirect(url_for("challenges.listing"))

    return plugin_bp

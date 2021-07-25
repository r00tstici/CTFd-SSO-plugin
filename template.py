import re

from CTFd.plugins import override_template


def update_template(app):
    environment = app.jinja_environment
    original = app.theme_loader.get_source(environment, 'login.html')[0]

    match = re.search(".*Forms\.auth\.LoginForm.*\n", original)
    if match:
        pos = match.start()

        injecting = """
			<a class="btn btn-secondary btn-lg btn-block" href="{{ url_for('sso.sso_oauth') }}">
				Log in with SSO
			</a>

			<hr>
        """

        new_template = original[:pos] + injecting + original[pos:]
        override_template('login.html', new_template)

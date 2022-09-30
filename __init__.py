from functools import wraps
from flask import g, request, redirect, url_for, session, render_template, abort


class CatapultAuth:
    def __init__(self, app=None):
        from jinja2 import Environment, PackageLoader
        self.jinja_env = Environment(
            autoescape=True,
            loader=PackageLoader(__name__, 'templates'))
        if app is not None:
            self.init_app(app)


    def init_app(self, app):
        import catapult_auth.ad_auth
        import catapult_auth.flask_requester
        from flask import render_template, redirect, url_for, Blueprint

        bp = Blueprint('myext', __name__, template_folder='templates', static_folder='resources')
        app.register_blueprint(bp)


        @app.before_request
        def before_request():
            pass

        @app.get('/')
        @login_required
        @roles_allowed(['Standard User'])
        def welcome():
            return render_template('welcome.html')

        @app.get('/auth/login')
        def login():
            if flask_requester.requester.input('error'):
                return render_template('login.html', error=True)
            return render_template('login.html')

        @app.post('/auth/login')
        def do_login():
            username = flask_requester.requester.input('username')
            password = flask_requester.requester.input('password')
            return ad_auth.ad_auth(username, password)

        @app.get("/logout")
        def do_logout():
            session.pop('username', None)
            return redirect(url_for('login'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = f"{request.endpoint.replace('.', '/')}.html"
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def roles_allowed(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') is None:
                return abort(403)
            accepted_roles_found = []
            for role in roles:
                if role == session.get('role'):
                    accepted_roles_found.append(role)
                    break
            if len(accepted_roles_found) != 0:
                return f(*args, **kwargs)
            else:
                return abort(403)
        return decorated_function
    return decorator


def roles_denied(roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') is None:
                return abort(403)
            denied_roles_found = []
            for role in roles:
                if role == session.get('role'):
                    denied_roles_found.append(role)
                    break
            if len(denied_roles_found) != 0:
                return abort(403)
            else:
                return f(*args, **kwargs)
        return decorated_function
    return decorator


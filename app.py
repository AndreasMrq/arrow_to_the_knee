# app.py
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required, UserMixin
from database import get_db, close_db, init_db_command

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'textadventure.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        if user is None:
            return None
        return User(user['id'], user['username'])

    # Register database functions
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    # Register blueprints
    from auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from game import bp as game_bp
    app.register_blueprint(game_bp)

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('game.index'))
        return redirect(url_for('auth.login'))

    return app

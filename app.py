import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from database import get_db, close_db, init_db_command
from user import User


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
            # Todo: Probably needs a better thing
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
        return User.from_db(db, user_id)

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

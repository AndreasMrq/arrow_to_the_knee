import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


    # Create new game
    db.execute(
        'INSERT INTO game (title, settings) VALUES (?, ?)',
        ("An arrow to the knee", "Some Settings")
    )
    game_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    users = [("Andi","Andi"),("Paddy", "Paddy")]
    for username, password in users:
        db.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (username, generate_password_hash(password))
        )
        user_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

        # Create character
        db.execute(
            'INSERT INTO character (user_id, name, description) VALUES (?, ?, ?)',
            (user_id, username, "A character without any particular notice")
        )
        character_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

    db.commit()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

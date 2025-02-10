from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from database import get_db
import json
from datetime import datetime

bp = Blueprint('game', __name__, url_prefix='/game')

@bp.route('/')
@login_required
def index():
    db = get_db()
    # Get current game if user is participating in one
    current_game = db.execute('''
        SELECT g.* FROM game g
        JOIN game_participant gp ON g.id = gp.game_id
        WHERE gp.user_id = ?
        ORDER BY g.created_at DESC LIMIT 1
    ''', (current_user.id,)).fetchone()
    
    if current_game:
        # Get game history with usernames
        history = db.execute('''
            SELECT ge.*, u.username
            FROM game_entry ge
            JOIN user u ON ge.user_id = u.id
            WHERE ge.game_id = ?
            ORDER BY ge.created_at ASC
        ''', (current_game['id'],)).fetchall()
        
        return render_template('game.html', current_game=current_game, history=history)
    
    return render_template('game.html', current_game=None)

@bp.route('/new', methods=['POST'])
@login_required
def new_game():
    if request.method == 'POST':
        title = request.form['title']
        character_name = request.form['character_name']
        character_description = request.form['character_description']
        settings = request.form['settings']
        
        db = get_db()
        error = None

        if not title:
            error = 'Title is required.'
        elif not character_name:
            error = 'Character name is required.'

        if error is None:
            try:
                # Create new game
                db.execute(
                    'INSERT INTO game (title, settings) VALUES (?, ?)',
                    (title, settings)
                )
                game_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                
                # Create character
                db.execute(
                    'INSERT INTO character (user_id, name, description) VALUES (?, ?, ?)',
                    (current_user.id, character_name, character_description)
                )
                character_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                
                # Add user as participant
                db.execute(
                    'INSERT INTO game_participant (game_id, user_id, character_id) VALUES (?, ?, ?)',
                    (game_id, current_user.id, character_id)
                )
                
                # Add initial game entry
                db.execute(
                    'INSERT INTO game_entry (game_id, user_id, content) VALUES (?, ?, ?)',
                    (game_id, current_user.id, f"Game started by {current_user.username}")
                )
                
                db.commit()
                return redirect(url_for('game.index'))
            
            except db.IntegrityError:
                error = "Error creating new game."
            
        flash(error)
    
    return redirect(url_for('game.index'))

@bp.route('/entry', methods=['POST'])
@login_required
def add_entry():
    content = request.form['content']
    
    if not content:
        flash('Content is required.')
        return redirect(url_for('game.index'))
    
    db = get_db()
    # Get current game
    current_game = db.execute('''
        SELECT g.* FROM game g
        JOIN game_participant gp ON g.id = gp.game_id
        WHERE gp.user_id = ?
        ORDER BY g.created_at DESC LIMIT 1
    ''', (current_user.id,)).fetchone()
    
    if current_game:
        db.execute(
            'INSERT INTO game_entry (game_id, user_id, content) VALUES (?, ?, ?)',
            (current_game['id'], current_user.id, content)
        )
        db.commit()
    
    return redirect(url_for('game.index'))

@bp.route('/join/<int:game_id>', methods=['POST'])
@login_required
def join_game():
    character_name = request.form['character_name']
    character_description = request.form['character_description']
    
    if not character_name:
        flash('Character name is required.')
        return redirect(url_for('game.index'))
    
    db = get_db()
    try:
        # Create character
        db.execute(
            'INSERT INTO character (user_id, name, description) VALUES (?, ?, ?)',
            (current_user.id, character_name, character_description)
        )
        character_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        
        # Add user as participant
        db.execute(
            'INSERT INTO game_participant (game_id, user_id, character_id) VALUES (?, ?, ?)',
            (game_id, current_user.id, character_id)
        )
        
        # Add join message
        db.execute(
            'INSERT INTO game_entry (game_id, user_id, content) VALUES (?, ?, ?)',
            (game_id, current_user.id, f"{current_user.username} joined the game as {character_name}")
        )
        
        db.commit()
    except db.IntegrityError:
        flash('Error joining game.')
    
    return redirect(url_for('game.index'))

@bp.route('/games', methods=['GET'])
@login_required
def list_games():
    db = get_db()
    games = db.execute('''
        SELECT g.*, COUNT(DISTINCT gp.user_id) as player_count
        FROM game g
        LEFT JOIN game_participant gp ON g.id = gp.game_id
        GROUP BY g.id
        ORDER BY g.created_at DESC
    ''').fetchall()
    
    return render_template('game_list.html', games=games)

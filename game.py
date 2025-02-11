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
        SELECT * FROM game
    ''', ()).fetchone()
    
    if current_game:
        # Get game history with usernames
        history = db.execute('''
            SELECT ge.*
            FROM game_entry ge
            WHERE ge.game_id = ?
            ORDER BY ge.created_at ASC
        ''', (current_game['id'],)).fetchall()
        
        return render_template('game.html', current_game=current_game, history=history)
    
    return render_template('game.html', current_game=None)

@bp.route('/game/<id>/entry', methods=['POST'])
@login_required
def add_entry(id):
    content = request.form['content']
    
    if not content:
        flash('Content is required.')
        return redirect(url_for('game.index'))
    
    db = get_db()
    # Get current game
    current_game = db.execute('''
        SELECT g.* FROM game g
        WHERE g.id = ?
    ''', (id)).fetchone()
    
    if current_game:
        db.execute(
            'INSERT INTO game_entry (game_id, user_id, content) VALUES (?, ?, ?)',
            (current_game['id'], current_user.id, content)
        )
        db.commit()
    
    return redirect(url_for('game.index'))

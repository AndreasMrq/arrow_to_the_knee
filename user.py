from flask_login import  UserMixin

class Character:
    def __init__(self, id:int, name:str, description: str):
        self.id = id
        self.name = name
        self.description = description

    @staticmethod
    def from_db(db, user_id: int) -> 'Character | None':
        character = db.execute(
            'SELECT * FROM character WHERE user_id = ?', (user_id,)
        ).fetchone()
        if character is None:
            return None
        return Character(character['id'], character['name'], character['description'])


class User(UserMixin):
    def __init__(self, id:int , username: str, character: Character):
        self.id = id
        self.username = username
        self.character = character

    @staticmethod
    def from_db(db, user_id: int) -> 'User | None':
        user = db.execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        character = Character.from_db(db, user_id)
        if user is None or character is None:
            return None
        return User(user['id'], user['username'], character)


import re
import bcrypt
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SECRET_KEY'] = "random string"

db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    game_mode = db.Column(db.String(100))
    level = db.Column(db.Integer)

    def __init__(self, email, username, password, game_mode="addition", level=1):
        # check if email is valid
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address.")
        self.email = email

        # check if username is valid
        if not re.match(r"^[A-Za-z0-9_]+$", username):
            raise ValueError("Invalid username. Must contain only letters, numbers and underscores.")
        self.username = username

        # check if password is valid
        if len(password) < 6:
            raise ValueError("Invalid password. Must be at least 6 characters long.")
        # encode the password for more security
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed_password.decode('utf-8')

        self.game_mode = game_mode
        self.level = level


class MedianValues(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, primary_key=True)
    game_mode = db.Column(db.String(100), primary_key=True)
    median = db.Column(db.Integer, nullable=False)
    last_score = db.Column(db.Integer)
    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, game_mode, median, last_score):
        self.user_id = user_id
        self.game_mode = game_mode
        self.median = median
        self.last_score = last_score


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_mode = db.Column(db.String(100))
    score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, game_mode, score):
        self.user_id = user_id
        self.game_mode = game_mode
        self.score = score


class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', foreign_keys=user_id)

    def __init__(self, user_id, score):
        self.user_id = user_id
        self.score = score


class AdditionLeaderboard(Leaderboard):
    __table_name__ = 'addition_leaderboard'
    id = db.Column(db.Integer, db.ForeignKey('leaderboard.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'addition_leaderboard'}


class SubtractionLeaderboard(Leaderboard):
    __table_name__ = 'subtraction_leaderboard'
    id = db.Column(db.Integer, db.ForeignKey('leaderboard.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'subtraction_leaderboard'}


class MultiplicationLeaderboard(Leaderboard):
    __table_name__ = 'multiplication_leaderboard'
    id = db.Column(db.Integer, db.ForeignKey('leaderboard.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'multiplication_leaderboard'}


class DivisionLeaderboard(Leaderboard):
    __table_name__ = 'division_leaderboard'
    id = db.Column(db.Integer, db.ForeignKey('leaderboard.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'division_leaderboard'}


def determine_leaderboard_table(game_mode):
    if game_mode == "addition":
        leaderboard_table = AdditionLeaderboard
    elif game_mode == "subtraction":
        leaderboard_table = SubtractionLeaderboard
    elif game_mode == "multiplication":
        leaderboard_table = MultiplicationLeaderboard
    elif game_mode == "division":
        leaderboard_table = DivisionLeaderboard
    else:
        raise ValueError("Game mode not set.")
    return leaderboard_table


def get_last_3_scores(game_mode, user_id):
    scores = db.session.query(Score).filter_by(game_mode=game_mode, user_id=user_id).all()
    return scores[-4:-1]


def get_last_score(game_mode, user_id):
    last_score = db.session.query(Score).filter_by(game_mode=game_mode, user_id=user_id).order_by(desc(Score.id)).first()
    return last_score.score


def get_all_last_scores(game_mode):
    scores = db.session.query(MedianValues.last_score).filter_by(game_mode=game_mode).order_by(MedianValues.user_id).all()
    median_list = []
    for med in scores:
        median_list.append(med[0])
    return median_list


def get_all_medians(game_mode):
    medians = db.session.query(MedianValues.median).filter_by(game_mode=game_mode).order_by(MedianValues.user_id).all()
    median_list = []
    for med in medians:
        median_list.append(med[0])
    return median_list


def get_count(game_mode):
    score_count = db.session.query(Score).filter_by(game_mode=game_mode).count()
    return score_count

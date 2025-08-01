from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Classe de base pour les statistiques (héritage)
class Statistics:
    def __init__(self, points=0, assists=0, rebounds=0, minutes=0):
        self.points = points
        self.assists = assists
        self.rebounds = rebounds
        self.minutes = minutes
    
    def get_efficiency_rating(self):
        """Calcule l'efficacité du joueur"""
        return (self.points + self.assists * 2 + self.rebounds * 1.5) / max(self.minutes, 1)

# Modèle utilisateur (hérite de UserMixin pour Flask-Login)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='user')  # user, admin, manager
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relation d'association avec les équipes (many-to-many)
    managed_teams = db.relationship('Team', secondary='user_team_association', back_populates='managers')
    
    # Relation d'agrégation avec les notifications (one-to-many)
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Modèle équipe
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    conference = db.Column(db.String(50))
    division = db.Column(db.String(50))
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation d'agrégation avec les joueurs (one-to-many)
    players = db.relationship('Player', backref='team', lazy=True, cascade='all, delete-orphan')
    
    # Relation d'association avec les utilisateurs (many-to-many)
    managers = db.relationship('User', secondary='user_team_association', back_populates='managed_teams')
    
    # Relation d'agrégation avec les matchs (one-to-many)
    home_games = db.relationship('Game', foreign_keys='Game.home_team_id', backref='home_team', lazy=True)
    away_games = db.relationship('Game', foreign_keys='Game.away_team_id', backref='away_team', lazy=True)

# Table d'association pour User-Team (relation many-to-many)
user_team_association = db.Table('user_team_association',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)

# Modèle joueur (hérite de Statistics)
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(20))
    height = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    birth_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    nba_debut = db.Column(db.Integer)
    jersey_number = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Statistiques (composition avec Statistics)
    points_per_game = db.Column(db.Float, default=0.0)
    assists_per_game = db.Column(db.Float, default=0.0)
    rebounds_per_game = db.Column(db.Float, default=0.0)
    minutes_per_game = db.Column(db.Float, default=0.0)
    
    # Relation d'agrégation avec les performances (one-to-many)
    performances = db.relationship('PlayerPerformance', backref='player', lazy=True, cascade='all, delete-orphan')
    
    def get_statistics(self):
        """Retourne un objet Statistics basé sur les données du joueur"""
        return Statistics(
            points=self.points_per_game,
            assists=self.assists_per_game,
            rebounds=self.rebounds_per_game,
            minutes=self.minutes_per_game
        )
    
    def update_statistics(self, stats):
        """Met à jour les statistiques du joueur"""
        self.points_per_game = stats.points
        self.assists_per_game = stats.assists
        self.rebounds_per_game = stats.rebounds
        self.minutes_per_game = stats.minutes

# Modèle match
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    home_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    away_team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, live, finished
    season = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation d'agrégation avec les performances (one-to-many)
    performances = db.relationship('PlayerPerformance', backref='game', lazy=True, cascade='all, delete-orphan')

# Modèle performance de joueur (hérite de Statistics)
class PlayerPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    minutes = db.Column(db.Integer, default=0)
    field_goals_made = db.Column(db.Integer, default=0)
    field_goals_attempted = db.Column(db.Integer, default=0)
    three_points_made = db.Column(db.Integer, default=0)
    three_points_attempted = db.Column(db.Integer, default=0)
    free_throws_made = db.Column(db.Integer, default=0)
    free_throws_attempted = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_statistics(self):
        """Retourne un objet Statistics basé sur cette performance"""
        return Statistics(
            points=self.points,
            assists=self.assists,
            rebounds=self.rebounds,
            minutes=self.minutes
        )

# Modèle notification
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')  # info, warning, success, error
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        self.is_read = True 
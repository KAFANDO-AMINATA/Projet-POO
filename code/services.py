import requests
import json
from datetime import datetime
from app import app, db, mail
from models import Team, Player, Game, PlayerPerformance, Notification, User
from flask_mail import Message
import os

class NBAApiService:
    """Service pour interagir avec l'API NBA"""
    
    def __init__(self):
        self.api_key = os.getenv('NBA_API_KEY')
        self.api_host = 'free-nba.p.rapidapi.com'
        self.base_url = 'https://free-nba.p.rapidapi.com'
        
    def _make_request(self, endpoint, params=None):
        """Effectue une requête vers l'API NBA"""
        headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': self.api_host
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur API NBA: {response.status_code}")
            return None
    
    def get_teams(self):
        """Récupère la liste des équipes"""
        data = self._make_request('teams')
        if data and 'data' in data:
            return data['data']
        return []
    
    def get_players(self, team_id=None):
        """Récupère la liste des joueurs"""
        params = {}
        if team_id:
            params['team_ids'] = team_id
            
        data = self._make_request('players', params)
        if data and 'data' in data:
            return data['data']
        return []
    
    def get_games(self, team_id=None, date=None):
        """Récupère les matchs"""
        params = {}
        if team_id:
            params['team_ids'] = team_id
        if date:
            params['dates[]'] = date
            
        data = self._make_request('games', params)
        if data and 'data' in data:
            return data['data']
        return []
    
    def get_player_stats(self, player_id, season=None):
        """Récupère les statistiques d'un joueur"""
        params = {'player_ids[]': player_id}
        if season:
            params['seasons[]'] = season
            
        data = self._make_request('stats', params)
        if data and 'data' in data:
            return data['data']
        return []

class NotificationService:
    """Service pour gérer les notifications"""
    
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info'):
        """Crée une nouvelle notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def send_email_notification(user_email, subject, body):
        """Envoie une notification par email"""
        try:
            msg = Message(
                subject=subject,
                recipients=[user_email],
                body=body,
                sender=app.config['MAIL_USERNAME']
            )
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Erreur envoi email: {e}")
            return False
    
    @staticmethod
    def send_push_notification(user_id, title, message):
        """Envoie une notification push (simulation)"""
        # Ici on pourrait intégrer Firebase Cloud Messaging ou autre service
        notification = NotificationService.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type='push'
        )
        return notification
    
    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        """Récupère les notifications d'un utilisateur"""
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """Marque une notification comme lue"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.mark_as_read()
            db.session.commit()
            return True
        return False

class DataSyncService:
    """Service pour synchroniser les données avec l'API NBA"""
    
    def __init__(self):
        self.nba_api = NBAApiService()
    
    def sync_teams(self):
        """Synchronise les équipes avec l'API"""
        teams_data = self.nba_api.get_teams()
        synced_count = 0
        
        for team_data in teams_data:
            team = Team.query.filter_by(name=team_data.get('name')).first()
            
            if not team:
                team = Team(
                    name=team_data.get('name'),
                    city=team_data.get('city'),
                    conference=team_data.get('conference'),
                    division=team_data.get('division')
                )
                db.session.add(team)
                synced_count += 1
            else:
                # Mise à jour des données existantes
                team.city = team_data.get('city')
                team.conference = team_data.get('conference')
                team.division = team_data.get('division')
        
        db.session.commit()
        return synced_count
    
    def sync_players(self, team_id=None):
        """Synchronise les joueurs avec l'API"""
        players_data = self.nba_api.get_players(team_id)
        synced_count = 0
        
        for player_data in players_data:
            player = Player.query.filter_by(name=player_data.get('name')).first()
            
            if not player:
                # Trouver l'équipe
                team = None
                if player_data.get('team'):
                    team = Team.query.filter_by(name=player_data['team'].get('name')).first()
                
                if team:
                    player = Player(
                        name=player_data.get('name'),
                        position=player_data.get('position'),
                        height=player_data.get('height'),
                        weight=player_data.get('weight'),
                        nationality=player_data.get('nationality'),
                        nba_debut=player_data.get('nba_debut'),
                        jersey_number=player_data.get('jersey_number'),
                        team_id=team.id
                    )
                    db.session.add(player)
                    synced_count += 1
        
        db.session.commit()
        return synced_count
    
    def sync_games(self, team_id=None):
        """Synchronise les matchs avec l'API"""
        games_data = self.nba_api.get_games(team_id)
        synced_count = 0
        
        for game_data in games_data:
            game = Game.query.filter_by(id=game_data.get('id')).first()
            
            if not game:
                # Trouver les équipes
                home_team = Team.query.filter_by(name=game_data.get('home_team', {}).get('name')).first()
                away_team = Team.query.filter_by(name=game_data.get('visitor_team', {}).get('name')).first()
                
                if home_team and away_team:
                    game = Game(
                        id=game_data.get('id'),
                        date=datetime.fromisoformat(game_data.get('date').replace('Z', '+00:00')),
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        home_score=game_data.get('home_team_score', 0),
                        away_score=game_data.get('visitor_team_score', 0),
                        status=game_data.get('status'),
                        season=game_data.get('season')
                    )
                    db.session.add(game)
                    synced_count += 1
        
        db.session.commit()
        return synced_count 
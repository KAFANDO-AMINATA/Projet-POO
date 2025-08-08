#!/usr/bin/env python3
"""
Application NBA Analytics - Main Entry Point
============================================
...
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app import app, db
from models import User, Team, Player, Game, PlayerPerformance, Notification
from services import NBAApiService, NotificationService, DataSyncService
from balldontlie_service import BalldontlieService
from datetime import datetime


def create_admin_user():
    """Crée un utilisateur administrateur par défaut si aucun n'existe"""
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@nba-analytics.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    admin = User.query.filter_by(email=admin_email).first()
    if not admin:
        admin = User(
            email=admin_email,
            name='Administrateur',
            role='admin'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Utilisateur administrateur créé: {admin_email}")


def init_database():
    """Initialise la base de données avec les équipes NBA réelles depuis balldontlie.io"""
    print("🔧 Initialisation de la base de données...")
    db.create_all()
    create_admin_user()

    print("📊 Synchronisation des équipes NBA depuis balldontlie.io...")
    teams_data = BalldontlieService.get_teams()

    for team_data in teams_data:
        team = Team(
            id=team_data['id'],
            name=team_data['full_name'],
            city=team_data['city'],
            conference=team_data['conference'],
            division=team_data['division'],
            logo_url=None,
            created_at=datetime.utcnow()
        )
        db.session.merge(team)  # remplace add pour éviter le conflit sur l'ID

    db.session.commit()
    print(f"✅ {len(teams_data)} équipes NBA synchronisées")
    print("✅ Base de données initialisée avec succès!")


    page = 1
    per_page = 100  # maximum autorisé par l'API
    has_more = True

    while has_more:
        players_data = BalldontlieService.get_players(page=page, per_page=per_page)
        players = players_data.get("data", [])

        for player_data in players:
            player = Player(
                id=player_data['id'],
                first_name=player_data['first_name'],
                last_name=player_data['last_name'],
                position=player_data['position'],
                team_id=player_data['team']['id'] if player_data['team'] else None,
                height_feet=player_data.get('height_feet'),
                height_inches=player_data.get('height_inches'),
                weight_pounds=player_data.get('weight_pounds'),
                created_at=datetime.utcnow()
            )
            db.session.merge(player)

        db.session.commit()

        # Vérifie s’il y a encore d’autres pages
        total_pages = players_data.get("meta", {}).get("total_pages", 1)
        if page < total_pages:
            page += 1
        else:
            has_more = False

    page = 1
    per_page = 100
    has_more = True
    season = get_current_nba_season()

    while has_more:
        games_data = BalldontlieService.get_games(season=season, page=page, per_page=per_page)
        games = games_data.get("data", [])

        for game_data in games:
            game = Game(
                id=game_data['id'],
                date=datetime.fromisoformat(game_data['date'].replace("Z", "+00:00")),
                season=game_data['season'],
                period=game_data['period'],
                status=game_data['status'],
                home_team_id=game_data['home_team']['id'] if game_data.get('home_team') else None,
                home_team_score=game_data['home_team_score'],
                visitor_team_id=game_data['visitor_team']['id'] if game_data.get('visitor_team') else None,
                visitor_team_score=game_data['visitor_team_score'],
                created_at=datetime.utcnow()
            )
            db.session.merge(game)

        db.session.commit()

        total_pages = games_data.get("meta", {}).get("total_pages", 1)
        if page < total_pages:
            page += 1
        else:
            has_more = False


def get_current_nba_season():
    """Retourne automatiquement la saison NBA en cours."""
    today = datetime.now()
    year = today.year
    month = today.month

    if month >= 10:  # Octobre, novembre, décembre
        return year
    elif month <= 6:  # Janvier à juin
        return year - 1
    else:
        return year - 1  # Été : on garde la dernière saison finie

# Exemple d'utilisation :
season = get_current_nba_season()
print(f"Saison NBA détectée : {season}")


def main():
    """Point d'entrée principal de l'application"""
    print("🏀 NBA Analytics - Démarrage de l'application...")

    required_vars = ['SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"⚠️  Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("💡 Créez un fichier .env avec les variables requises")
        return

    with app.app_context():
        init_database()

    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"🚀 Application démarrée sur http://{host}:{port}")
    print("📧 Email admin par défaut: admin@nba-analytics.com")
    print("🔑 Mot de passe admin par défaut: admin123")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()

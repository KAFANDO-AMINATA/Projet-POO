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

    
# Pagination initiale
    page = 1
    per_page = 100  # maximum autorisé par l'API
    has_more = True

    while has_more:
        players_data = BalldontlieService.get_players(page=page, per_page=per_page)
        players = players_data.get("data", [])

        for p in players:
            # Récupération des stats d'un joueur via l'API
            stats_data = BalldontlieService.get_player_stats(player_id=p['id'])
            
            # Valeurs par défaut si pas de stats
            points = assists = rebounds = minutes = 0.0

            if stats_data.get("data"):
                last_stat = stats_data["data"][-1]  # Dernier match dispo
                points = last_stat.get("pts", 0.0)
                assists = last_stat.get("ast", 0.0)
                rebounds = last_stat.get("reb", 0.0)
                minutes = float(last_stat.get("min", "0").split(":")[0]) if last_stat.get("min") else 0.0

            player = Player(
                id=p['id'],
                first_name=p['first_name'],
                last_name=p['last_name'],
                position=p['position'],
                team_id=p['team']['id'] if p.get('team') else None,
                height_feet=p.get('height_feet'),
                height_inches=p.get('height_inches'),
                weight_pounds=p.get('weight_pounds'),
                points_per_game=points,
                assists_per_game=assists,
                rebounds_per_game=rebounds,
                minutes_per_game=minutes,
                created_at=datetime.utcnow()
            )

            db.session.merge(player)

        db.session.commit()

        # Pagination
        total_pages = players_data.get("meta", {}).get("total_pages", 1)
        has_more = page < total_pages
        page += 1

    print("✅ Joueurs et statistiques synchronisés avec succès.")



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

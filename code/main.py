#!/usr/bin/env python3
"""
Application NBA Analytics - Main Entry Point
============================================

Cette application permet aux managers d'équipes NBA de gérer et analyser
les données de leurs équipes et joueurs.

Fonctionnalités principales :
- Authentification utilisateur (email + Google OAuth)
- Gestion des équipes et joueurs
- Analyse des statistiques
- Système de notifications
- Synchronisation avec l'API NBA
"""

import os
import sys
from dotenv import load_dotenv

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Charger les variables d'environnement
load_dotenv()

# Importer l'application Flask
from app import app, db
from models import User, Team, Player, Game, PlayerPerformance, Notification
from services import NBAApiService, NotificationService, DataSyncService

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
    """Initialise la base de données avec des données de test"""
    print("🔧 Initialisation de la base de données...")
    
    # Créer les tables
    db.create_all()
    
    # Créer l'utilisateur admin
    create_admin_user()
    
    # Ajouter quelques équipes de test si la base est vide
    if Team.query.count() == 0:
        print("📊 Ajout d'équipes de test...")
        teams_data = [
            {'name': 'Lakers', 'city': 'Los Angeles', 'conference': 'Western', 'division': 'Pacific'},
            {'name': 'Celtics', 'city': 'Boston', 'conference': 'Eastern', 'division': 'Atlantic'},
            {'name': 'Bulls', 'city': 'Chicago', 'conference': 'Eastern', 'division': 'Central'},
            {'name': 'Warriors', 'city': 'Golden State', 'conference': 'Western', 'division': 'Pacific'},
        ]
        
        for team_data in teams_data:
            team = Team(**team_data)
            db.session.add(team)
        
        db.session.commit()
        print(f"✅ {len(teams_data)} équipes de test ajoutées")
    
    print("✅ Base de données initialisée avec succès!")

def main():
    """Point d'entrée principal de l'application"""
    print("🏀 NBA Analytics - Démarrage de l'application...")
    
    # Vérifier les variables d'environnement requises
    required_vars = ['SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Variables d'environnement manquantes: {', '.join(missing_vars)}")
        print("💡 Créez un fichier .env avec les variables requises")
        return
    
    # Initialiser la base de données
    with app.app_context():
        init_database()
    
    # Démarrer l'application
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Application démarrée sur http://{host}:{port}")
    print("📧 Email admin par défaut: admin@nba-analytics.com")
    print("🔑 Mot de passe admin par défaut: admin123")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main() 
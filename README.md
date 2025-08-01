# 🏀 NBA Analytics - Application d'Analyse de Données NBA

Une application web complète pour l'analyse et la gestion des données NBA, développée en Python avec Flask et une architecture orientée objet.

## 📋 Fonctionnalités

### ✅ Fonctionnalités MVP
- **Authentification** : Système de connexion par email
- **Notifications** : Système de notifications push et internes
- **Gestion des équipes** : Liste et détails des équipes NBA
- **Gestion des joueurs** : Profils, statistiques et ajout de joueurs
- **Analyse des matchs** : Suivi des résultats et performances
- **Synchronisation API** : Intégration avec l'API NBA RapidAPI

### 🔧 Architecture Orientée Objet

L'application respecte les principes de la POO avec :

#### Classes principales (5+ classes) :
1. **User** - Gestion des utilisateurs (hérite de UserMixin)
2. **Team** - Gestion des équipes
3. **Player** - Gestion des joueurs
4. **Game** - Gestion des matchs
5. **PlayerPerformance** - Gestion des performances
6. **Notification** - Système de notifications
7. **Statistics** - Classe utilitaire pour les statistiques

#### Relations orientées objet :
- **Héritage** : `User` hérite de `UserMixin` (Flask-Login)
- **Association** : `User` ↔ `Team` (many-to-many via `user_team_association`)
- **Agrégation/Composition** : `Team` → `Player` (one-to-many), `Player` → `PlayerPerformance`

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.8+
- pip

### Installation

1. **Cloner le repository**
```bash
git clone <repository-url>
cd Projet-POO/code
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configuration des variables d'environnement**
```bash
# Copier le fichier d'exemple
cp env_example.txt .env

# Éditer le fichier .env avec vos configurations
# Au minimum, définissez SECRET_KEY
```

4. **Lancer l'application**
```bash
python main.py
```

5. **Accéder à l'application**
- URL : http://localhost:5000
- Compte admin par défaut : admin@nba-analytics.com / admin123

## 📊 Fonctionnalités Détaillées

### 🔐 Authentification
- Inscription/Connexion par email
- Gestion des sessions utilisateur
- Rôles utilisateur (user, admin, manager)

### 📈 Dashboard
- Statistiques en temps réel
- Vue d'ensemble des équipes et joueurs
- Actions rapides
- Notifications non lues

### 🏀 Gestion des Équipes
- Liste complète des équipes NBA
- Détails par équipe (ville, conférence, division)
- Joueurs par équipe
- Historique des matchs

### 👤 Gestion des Joueurs
- Profils détaillés des joueurs
- Statistiques (points, passes, rebonds par match)
- Filtres par équipe et position
- Ajout de nouveaux joueurs

### 🎮 Gestion des Matchs
- Historique des matchs
- Scores et statuts
- Performances des joueurs
- Filtres par équipe

### 🔔 Système de Notifications
- Notifications en temps réel
- Types : info, success, warning, error
- Marquer comme lu
- Notifications push (simulation)

### 🔄 Synchronisation API
- Intégration avec l'API NBA RapidAPI
- Synchronisation automatique des données
- Gestion des erreurs API

## 🏗️ Architecture Technique

### Backend
- **Framework** : Flask
- **Base de données** : SQLite (SQLAlchemy ORM)
- **Authentification** : Flask-Login
- **API** : RESTful avec JSON

### Frontend
- **Framework CSS** : Bootstrap 5
- **Icônes** : Font Awesome
- **JavaScript** : Vanilla JS
- **Design** : Responsive et moderne

### Structure des Fichiers
```
code/
├── main.py              # Point d'entrée principal
├── app.py              # Configuration Flask
├── models.py           # Modèles de données
├── routes.py           # Routes de l'application
├── services.py         # Services (API, notifications)
├── requirements.txt    # Dépendances Python
├── env_example.txt    # Variables d'environnement
└── templates/         # Templates HTML
    ├── base.html
    ├── index.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── teams.html
    └── players.html
```

## 🔧 Configuration Avancée

### Variables d'Environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `SECRET_KEY` | Clé secrète Flask | ✅ |
| `FLASK_ENV` | Environnement (development/production) | ❌ |
| `HOST` | Hôte de l'application | ❌ |
| `PORT` | Port de l'application | ❌ |
| `MAIL_USERNAME` | Email pour notifications | ❌ |
| `MAIL_PASSWORD` | Mot de passe email | ❌ |
| `GOOGLE_CLIENT_ID` | ID client Google OAuth | ❌ |
| `GOOGLE_CLIENT_SECRET` | Secret client Google OAuth | ❌ |
| `NBA_API_KEY` | Clé API RapidAPI NBA | ❌ |

### API NBA
L'application utilise l'API NBA de RapidAPI :
- Endpoint : https://rapidapi.com/theapiguy/api/free-nba/
- Fonctionnalités : Équipes, joueurs, matchs, statistiques

## 🧪 Tests

### Tests Manuels
1. **Authentification** : Test d'inscription et connexion
2. **Dashboard** : Vérification des statistiques
3. **Équipes** : Navigation et affichage
4. **Joueurs** : Filtres et ajout
5. **Notifications** : Création et lecture
6. **Synchronisation** : Test de l'API NBA

### Comptes de Test
- **Admin** : admin@nba-analytics.com / admin123
- **Utilisateur** : Créer via l'interface d'inscription

## 🚀 Déploiement

### Développement Local
```bash
python main.py
```

### Production (avec Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

## 📝 Licence

Ce projet est développé dans le cadre d'un projet de programmation orientée objet.

## 👥 Auteur

Développé avec ❤️ pour l'analyse de données NBA.

---

**Note** : Cette application est prête pour les tests utilisateurs et peut être étendue avec des fonctionnalités supplémentaires selon les besoins.
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, Team, Player, Game, PlayerPerformance, Notification
from services import NBAApiService, NotificationService, DataSyncService
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Services
nba_api = NBAApiService()
notification_service = NotificationService()
data_sync = DataSyncService()

@app.route('/test')
def test():
    """Route de test pour vérifier le rendu des templates"""
    return render_template('test.html')

@app.route('/')
def index():
    """Page d'accueil"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'error')
            return render_template('register.html')
        
        user = User(email=email, name=name)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    # Statistiques pour le dashboard
    total_teams = Team.query.count()
    total_players = Player.query.count()
    recent_games = Game.query.order_by(Game.date.desc()).limit(5).all()
    
    # Notifications non lues
    unread_notifications = NotificationService.get_user_notifications(
        current_user.id, unread_only=True
    )
    
    return render_template('dashboard.html',
                         total_teams=total_teams,
                         total_players=total_players,
                         recent_games=recent_games,
                         unread_notifications=unread_notifications)

@app.route('/teams')
@login_required
def teams():
    """Liste des équipes"""
    teams = Team.query.all()
    return render_template('teams.html', teams=teams)

@app.route('/team/<int:team_id>')
@login_required
def team_detail(team_id):
    """Détails d'une équipe"""
    team = Team.query.get_or_404(team_id)
    players = Player.query.filter_by(team_id=team_id).all()
    games = Game.query.filter(
        (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
    ).order_by(Game.date.desc()).limit(10).all()
    
    return render_template('team_detail.html', team=team, players=players, games=games)

@app.route('/players')
@login_required
def players():
    """Liste des joueurs"""
    team_id = request.args.get('team_id', type=int)
    if team_id:
        players = Player.query.filter_by(team_id=team_id).all()
    else:
        players = Player.query.all()
    
    teams = Team.query.all()
    return render_template('players.html', players=players, teams=teams, selected_team=team_id)

@app.route('/player/<int:player_id>')
@login_required
def player_detail(player_id):
    """Détails d'un joueur"""
    player = Player.query.get_or_404(player_id)
    performances = PlayerPerformance.query.filter_by(player_id=player_id).order_by(PlayerPerformance.created_at.desc()).limit(10).all()
    
    return render_template('player_detail.html', player=player, performances=performances)

@app.route('/games')
@login_required
def games():
    """Liste des matchs"""
    team_id = request.args.get('team_id', type=int)
    if team_id:
        games = Game.query.filter(
            (Game.home_team_id == team_id) | (Game.away_team_id == team_id)
        ).order_by(Game.date.desc()).all()
    else:
        games = Game.query.order_by(Game.date.desc()).all()
    
    teams = Team.query.all()
    return render_template('games.html', games=games, teams=teams, selected_team=team_id)

@app.route('/add_player', methods=['GET', 'POST'])
@login_required
def add_player():
    """Ajouter un nouveau joueur"""
    if request.method == 'POST':
        name = request.form.get('name')
        position = request.form.get('position')
        team_id = request.form.get('team_id')
        jersey_number = request.form.get('jersey_number')
        
        if not name or not team_id:
            flash('Tous les champs obligatoires doivent être remplis.', 'error')
            return render_template('add_player.html', teams=Team.query.all())
        
        player = Player(
            name=name,
            position=position,
            team_id=team_id,
            jersey_number=jersey_number
        )
        
        db.session.add(player)
        db.session.commit()
        
        # Créer une notification
        NotificationService.create_notification(
            current_user.id,
            'Nouveau joueur ajouté',
            f'Le joueur {name} a été ajouté à l\'équipe.',
            'success'
        )
        
        flash('Joueur ajouté avec succès!', 'success')
        return redirect(url_for('players'))
    
    return render_template('add_player.html', teams=Team.query.all())

@app.route('/sync_data')
@login_required
def sync_data():
    """Synchroniser les données avec l'API NBA"""
    try:
        teams_synced = data_sync.sync_teams()
        players_synced = data_sync.sync_players()
        games_synced = data_sync.sync_games()
        
        flash(f'Synchronisation terminée: {teams_synced} équipes, {players_synced} joueurs, {games_synced} matchs', 'success')
        
        # Notification
        NotificationService.create_notification(
            current_user.id,
            'Synchronisation terminée',
            f'Données synchronisées: {teams_synced} équipes, {players_synced} joueurs, {games_synced} matchs',
            'info'
        )
        
    except Exception as e:
        flash(f'Erreur lors de la synchronisation: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/notifications')
@login_required
def notifications():
    """Page des notifications"""
    notifications = NotificationService.get_user_notifications(current_user.id)
    return render_template('notifications.html', notifications=notifications)

@app.route('/notifications/mark_read/<int:notification_id>')
@login_required
def mark_notification_read(notification_id):
    """Marquer une notification comme lue"""
    NotificationService.mark_notification_as_read(notification_id)
    return jsonify({'success': True})

@app.route('/api/notifications/unread')
@login_required
def api_unread_notifications():
    """API pour récupérer les notifications non lues"""
    notifications = NotificationService.get_user_notifications(current_user.id, unread_only=True)
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'created_at': n.created_at.isoformat()
    } for n in notifications])

@app.route('/profile')
@login_required
def profile():
    """Profil utilisateur"""
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Modifier le profil"""
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        
        db.session.commit()
        flash('Profil mis à jour avec succès!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=current_user)

# Routes API pour les données
@app.route('/api/teams')
@login_required
def api_teams():
    """API pour récupérer les équipes"""
    teams = Team.query.all()
    return jsonify([{
        'id': team.id,
        'name': team.name,
        'city': team.city,
        'conference': team.conference,
        'division': team.division
    } for team in teams])

@app.route('/api/players')
@login_required
def api_players():
    """API pour récupérer les joueurs"""
    team_id = request.args.get('team_id', type=int)
    if team_id:
        players = Player.query.filter_by(team_id=team_id).all()
    else:
        players = Player.query.all()
    
    return jsonify([{
        'id': player.id,
        'name': player.name,
        'position': player.position,
        'team_id': player.team_id,
        'points_per_game': player.points_per_game,
        'assists_per_game': player.assists_per_game,
        'rebounds_per_game': player.rebounds_per_game
    } for player in players])

@app.route('/api/games')
@login_required
def api_games():
    """API pour récupérer les matchs"""
    games = Game.query.order_by(Game.date.desc()).limit(20).all()
    return jsonify([{
        'id': game.id,
        'date': game.date.isoformat(),
        'home_team': game.home_team.name,
        'away_team': game.away_team.name,
        'home_score': game.home_score,
        'away_score': game.away_score,
        'status': game.status
    } for game in games]) 
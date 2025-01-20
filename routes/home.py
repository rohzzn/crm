from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from models import Client

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    if current_user.is_authenticated:
        clients = Client.query.filter_by(agent_id=current_user.id).all()
        num_clients = len(clients)
        return render_template('home.html', num_clients=num_clients)
    else:
        return redirect(url_for('auth.login')) 
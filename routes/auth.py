from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from models import db, Agent
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        
        if Agent.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        agent = Agent(email=email, password=hashed_password)
        db.session.add(agent)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        agent = Agent.query.filter_by(email=email).first()
        
        if agent and bcrypt.check_password_hash(agent.password, password):
            login_user(agent)
            return redirect(url_for('home.index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index')) 
from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from models import db, Agent
from routes.client import client_bp
from routes.auth import auth_bp
from routes.home import home_bp
from routes.policy import policy_bp
from routes.assigned import assigned_bp
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Agent, int(user_id))

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(policy_bp)
    app.register_blueprint(assigned_bp)

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

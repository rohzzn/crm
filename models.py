from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from dateutil.relativedelta import relativedelta

db = SQLAlchemy()

class Agent(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clients = db.relationship('Client', backref='agent', lazy=True)
    dependents = db.relationship('Dependent', backref='agent', lazy=True)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    sex = db.Column(db.String(10))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    dependents = db.relationship('Dependent', backref='client', lazy=True, cascade='all, delete-orphan')

    @hybrid_property
    def age(self):
        if self.date_of_birth:
            return relativedelta(datetime.now(), self.date_of_birth).years
        return None

    @hybrid_property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

class Dependent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    sex = db.Column(db.String(10))
    relationship = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)

    @hybrid_property
    def age(self):
        if self.date_of_birth:
            return relativedelta(datetime.now(), self.date_of_birth).years
        return None

    @hybrid_property
    def full_name(self):
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

class Policy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_group = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)

    def __repr__(self):
        return f'<Policy {self.name}>'

# Association table for assigned policies and dependents
assigned_policy_dependents = db.Table('assigned_policy_dependents',
    db.Column('assigned_policy_id', db.Integer, db.ForeignKey('assigned_policy.id'), primary_key=True),
    db.Column('dependent_id', db.Integer, db.ForeignKey('dependent.id'), primary_key=True)
)

class AssignedPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    premium_amount = db.Column(db.Float, nullable=False)
    tenure_months = db.Column(db.Integer, nullable=False)
    payment_cycle = db.Column(db.String(20), nullable=False)  # monthly, quarterly, yearly
    first_receipt_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    policy = db.relationship('Policy', backref='assigned_policies')
    client = db.relationship('Client', backref='assigned_policies')
    agent = db.relationship('Agent', backref='assigned_policies')
    dependents = db.relationship('Dependent', secondary=assigned_policy_dependents,
                               backref=db.backref('assigned_policies', lazy='dynamic'))

    @hybrid_property
    def is_active(self):
        return datetime.now().date() <= self.expiry_date

    def __repr__(self):
        return f'<AssignedPolicy {self.policy.name} - {self.client.full_name}>' 
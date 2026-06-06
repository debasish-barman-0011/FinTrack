from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import func, Numeric
from decimal import Decimal

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_password_change = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    incomes = db.relationship('Income', backref='user', lazy='dynamic')
    expenses = db.relationship('Expense', backref='user', lazy='dynamic')
    savings = db.relationship('Saving', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def is_password_expired(self):
        if not self.last_password_change:
            return True
        days_since_change = (datetime.utcnow() - self.last_password_change).days
        from config import Config
        return days_since_change >= Config.PASSWORD_EXPIRY_DAYS

class Income(db.Model):
    __tablename__ = 'income'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    amount = db.Column(Numeric(12, 2), nullable=False)
    remarks = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    INCOME_SOURCES = ['Salary', 'Freelancing', 'Government Scheme', 'Business', 'Other']

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(Numeric(12, 2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    EXPENSE_CATEGORIES = [
        'Grocery', 'Rice', 'Gas (Cooking)', 'Electricity', 
        'Weekly Bazar', 'Garments & Self Care', 'Medicine', 
        'Meat / Egg / Fish', 'Other'
    ]

class Saving(db.Model):
    __tablename__ = 'savings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(50))
    amount = db.Column(Numeric(12, 2), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    is_recovered = db.Column(db.Boolean, default=False)
    recovery_date = db.Column(db.Date)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)
    
    SAVINGS_CATEGORIES = ['Hard Cash at Home', 'Bank Deposit', 'Borrowed to Others', 'Investment', 'Other']
    INVESTMENT_SUB_CATEGORIES = ['Mutual Funds', 'Fixed Deposit', 'Gold', 'Stocks', 'PPF', 'NPS', 'Other']
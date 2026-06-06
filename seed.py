#!/usr/bin/env python
"""
Seed database with default admin user and sample data
"""
import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, User, Income, Expense, Saving

def seed_database():
    app = create_app()
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()
        
        # Create admin user
        admin = User(username='fucker')
        admin.set_password('fuckyoudear')
        admin.last_password_change = datetime.now()
        db.session.add(admin)
        db.session.flush()
        
        # Sample income data (last 3 months)
        today = date.today()
        income_data = [
            {'user_id': admin.id, 'source': 'Salary', 'amount': 50000, 'remarks': 'Monthly salary', 
             'date': today - timedelta(days=30)},
            {'user_id': admin.id, 'source': 'Freelancing', 'amount': 15000, 'remarks': 'Web development project', 
             'date': today - timedelta(days=25)},
            {'user_id': admin.id, 'source': 'Business', 'amount': 8000, 'remarks': 'Online sales', 
             'date': today - timedelta(days=20)},
            {'user_id': admin.id, 'source': 'Salary', 'amount': 50000, 'remarks': 'Monthly salary', 
             'date': today - timedelta(days=60)},
            {'user_id': admin.id, 'source': 'Freelancing', 'amount': 10000, 'remarks': 'Consulting', 
             'date': today - timedelta(days=55)},
        ]
        
        for data in income_data:
            income = Income(**data)
            db.session.add(income)
        
        # Sample expense data
        expense_data = [
            {'user_id': admin.id, 'category': 'Grocery', 'description': 'Weekly groceries', 'amount': 3500, 
             'date': today - timedelta(days=2)},
            {'user_id': admin.id, 'category': 'Electricity', 'description': 'Monthly electricity bill', 'amount': 1200, 
             'date': today - timedelta(days=5)},
            {'user_id': admin.id, 'category': 'Medicine', 'description': 'Pharmacy', 'amount': 450, 
             'date': today - timedelta(days=7)},
            {'user_id': admin.id, 'category': 'Garments & Self Care', 'description': 'Clothing', 'amount': 2500, 
             'date': today - timedelta(days=10)},
            {'user_id': admin.id, 'category': 'Gas (Cooking)', 'description': 'Gas cylinder refill', 'amount': 850, 
             'date': today - timedelta(days=12)},
            {'user_id': admin.id, 'category': 'Grocery', 'description': 'Monthly groceries', 'amount': 3800, 
             'date': today - timedelta(days=15)},
            {'user_id': admin.id, 'category': 'Weekly Bazar', 'description': 'Vegetables and fruits', 'amount': 600, 
             'date': today - timedelta(days=3)},
        ]
        
        for data in expense_data:
            expense = Expense(**data)
            db.session.add(expense)
        
        # Sample savings data
        savings_data = [
            {'user_id': admin.id, 'category': 'Bank Deposit', 'amount': 25000, 'remarks': 'Emergency fund', 
             'date': today - timedelta(days=45)},
            {'user_id': admin.id, 'category': 'Investment', 'sub_category': 'Mutual Funds', 'amount': 10000, 
             'remarks': 'SIP investment', 'date': today - timedelta(days=30)},
            {'user_id': admin.id, 'category': 'Borrowed to Others', 'amount': 5000, 'remarks': 'Loaned to Rajesh, due next month', 
             'date': today - timedelta(days=15), 'is_recovered': False},
            {'user_id': admin.id, 'category': 'Hard Cash at Home', 'amount': 15000, 'remarks': 'Cash savings at home', 
             'date': today - timedelta(days=10)},
            {'user_id': admin.id, 'category': 'Investment', 'sub_category': 'Fixed Deposit', 'amount': 50000, 
             'remarks': 'FD with 7% interest', 'date': today - timedelta(days=90)},
        ]
        
        for data in savings_data:
            saving = Saving(**data)
            db.session.add(saving)
        
        # Commit all changes
        db.session.commit()
        
        print("Database seeded successfully!")
        print("\nDefault Admin Credentials:")
        print("Username: fucker")
        print("Password: fuckyoudear")
        print("\nSample data has been added for testing.")

if __name__ == '__main__':
    seed_database()

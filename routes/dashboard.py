from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from balance import compute_balance, compute_monthly_trend
from models import db, Income, Expense, Saving
from datetime import datetime, date
from sqlalchemy import func, and_
from decimal import Decimal

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    # Get current month's data
    today = date.today()
    first_day_of_month = date(today.year, today.month, 1)
    
    # Current month income
    monthly_income = db.session.query(func.sum(Income.amount)).filter(
        and_(
            Income.user_id == current_user.id,
            Income.is_deleted == False,
            Income.date >= first_day_of_month,
            Income.date <= today
        )
    ).scalar() or Decimal('0')
    
    # Current month expenses
    monthly_expenses = db.session.query(func.sum(Expense.amount)).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.is_deleted == False,
            Expense.date >= first_day_of_month,
            Expense.date <= today
        )
    ).scalar() or Decimal('0')
    
    # Current month borrowed (unrecovered)
    monthly_borrowed = db.session.query(func.sum(Saving.amount)).filter(
        and_(
            Saving.user_id == current_user.id,
            Saving.category == 'Borrowed to Others',
            Saving.is_recovered == False,
            Saving.is_deleted == False,
            Saving.date <= today
        )
    ).scalar() or Decimal('0')
    
    # Net balance
    net_balance = monthly_income - monthly_expenses - monthly_borrowed
    
    # Total savings/assets
    total_savings = db.session.query(func.sum(Saving.amount)).filter(
        and_(
            Saving.user_id == current_user.id,
            Saving.is_deleted == False,
            Saving.date <= today
        )
    ).scalar() or Decimal('0')
    
    # Monthly trend data
    trend_data = compute_monthly_trend(current_user.id)
    
    # Expense breakdown for current month
    expense_breakdown = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        and_(
            Expense.user_id == current_user.id,
            Expense.is_deleted == False,
            Expense.date >= first_day_of_month,
            Expense.date <= today
        )
    ).group_by(Expense.category).all()
    
    expense_breakdown_data = [
        {'category': e.category, 'total': float(e.total)} 
        for e in expense_breakdown
    ]
    
    # Income breakdown for current month
    income_breakdown = db.session.query(
        Income.source,
        func.sum(Income.amount).label('total')
    ).filter(
        and_(
            Income.user_id == current_user.id,
            Income.is_deleted == False,
            Income.date >= first_day_of_month,
            Income.date <= today
        )
    ).group_by(Income.source).all()
    
    income_breakdown_data = [
        {'source': i.source, 'total': float(i.total)} 
        for i in income_breakdown
    ]
    
    return render_template('admin/dashboard.html',
                         monthly_income=float(monthly_income),
                         monthly_expenses=float(monthly_expenses),
                         net_balance=float(net_balance),
                         total_savings=float(total_savings),
                         trend_data=trend_data,
                         expense_breakdown=expense_breakdown_data,
                         income_breakdown=income_breakdown_data)

@dashboard_bp.route('/quick-add', methods=['POST'])
@login_required
def quick_add():
    from flask import request, flash, redirect, url_for
    
    entry_type = request.form.get('type')
    
    if entry_type == 'income':
        from routes.income import create_income_record
        return create_income_record()
    elif entry_type == 'expense':
        from routes.expenses import create_expense_record
        return create_expense_record()
    
    flash('Invalid entry type', 'danger')
    return redirect(url_for('dashboard.dashboard'))
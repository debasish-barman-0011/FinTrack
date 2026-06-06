from decimal import Decimal
from models import db, Income, Expense, Saving
from sqlalchemy import and_
from datetime import date

def compute_balance(user_id, as_of_date=None):
    """
    Compute comprehensive balance for a user
    
    Returns:
        dict: Contains total_income, total_expenses, total_borrowed_unrecovered, 
              net_available, total_savings
    """
    if as_of_date is None:
        as_of_date = date.today()
    
    # Total Income (not deleted, up to as_of_date)
    total_income = db.session.query(db.func.sum(Income.amount)).filter(
        and_(
            Income.user_id == user_id,
            Income.is_deleted == False,
            Income.date <= as_of_date
        )
    ).scalar() or Decimal('0')
    
    # Total Expenses (not deleted, up to as_of_date)
    total_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
        and_(
            Expense.user_id == user_id,
            Expense.is_deleted == False,
            Expense.date <= as_of_date
        )
    ).scalar() or Decimal('0')
    
    # Total Borrowed to Others (unrecovered, not deleted, up to as_of_date)
    total_borrowed = db.session.query(db.func.sum(Saving.amount)).filter(
        and_(
            Saving.user_id == user_id,
            Saving.category == 'Borrowed to Others',
            Saving.is_recovered == False,
            Saving.is_deleted == False,
            Saving.date <= as_of_date
        )
    ).scalar() or Decimal('0')
    
    # Total Savings (all categories, not deleted, up to as_of_date)
    total_savings = db.session.query(db.func.sum(Saving.amount)).filter(
        and_(
            Saving.user_id == user_id,
            Saving.is_deleted == False,
            Saving.date <= as_of_date
        )
    ).scalar() or Decimal('0')
    
    # Net Available Balance
    net_available = total_income - total_expenses - total_borrowed
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_borrowed_out_unrecovered': total_borrowed,
        'net_available': net_available,
        'total_savings': total_savings
    }

def compute_monthly_trend(user_id, months=12):
    """Compute monthly income vs expenses trend for last N months"""
    from datetime import datetime, timedelta
    from calendar import monthrange
    
    trend_data = []
    current_date = datetime.now().date()
    
    for i in range(months - 1, -1, -1):
        # Calculate month boundaries
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
        
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # Get monthly totals
        monthly_income = db.session.query(db.func.sum(Income.amount)).filter(
            and_(
                Income.user_id == user_id,
                Income.is_deleted == False,
                Income.date >= start_date,
                Income.date <= end_date
            )
        ).scalar() or Decimal('0')
        
        monthly_expenses = db.session.query(db.func.sum(Expense.amount)).filter(
            and_(
                Expense.user_id == user_id,
                Expense.is_deleted == False,
                Expense.date >= start_date,
                Expense.date <= end_date
            )
        ).scalar() or Decimal('0')
        
        trend_data.append({
            'month': start_date.strftime('%b %Y'),
            'income': float(monthly_income),
            'expenses': float(monthly_expenses)
        })
    
    return trend_data
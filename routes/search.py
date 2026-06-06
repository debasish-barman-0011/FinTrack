from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, Income, Expense, Saving
from sqlalchemy import or_, and_

search_bp = Blueprint('search', __name__)

@search_bp.route('/')
@login_required
def index():
    query = request.args.get('q', '')
    search_results = []
    
    if query:
        # Search in Income
        incomes = Income.query.filter(
            Income.user_id == current_user.id,
            Income.is_deleted == False,
            or_(
                Income.source.contains(query),
                Income.remarks.contains(query),
                Income.amount == query if query.replace('.', '').isdigit() else False
            )
        ).limit(20).all()
        
        for inc in incomes:
            search_results.append({
                'type': 'income',
                'id': inc.id,
                'date': inc.date.isoformat(),
                'title': inc.source,
                'description': inc.remarks or 'No remarks',
                'amount': float(inc.amount)
            })
        
        # Search in Expenses
        expenses = Expense.query.filter(
            Expense.user_id == current_user.id,
            Expense.is_deleted == False,
            or_(
                Expense.category.contains(query),
                Expense.description.contains(query),
                Expense.amount == query if query.replace('.', '').isdigit() else False
            )
        ).limit(20).all()
        
        for exp in expenses:
            search_results.append({
                'type': 'expense',
                'id': exp.id,
                'date': exp.date.isoformat(),
                'title': exp.category,
                'description': exp.description,
                'amount': float(exp.amount)
            })
        
        # Search in Savings
        savings = Saving.query.filter(
            Saving.user_id == current_user.id,
            Saving.is_deleted == False,
            or_(
                Saving.category.contains(query),
                Saving.sub_category.contains(query),
                Saving.remarks.contains(query),
                Saving.amount == query if query.replace('.', '').isdigit() else False
            )
        ).limit(20).all()
        
        for sav in savings:
            search_results.append({
                'type': 'saving',
                'id': sav.id,
                'date': sav.date.isoformat(),
                'title': sav.category,
                'description': sav.remarks,
                'amount': float(sav.amount),
                'recovered': sav.is_recovered
            })
        
        # Sort by date (most recent first)
        search_results.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('admin/search.html', query=query, results=search_results)
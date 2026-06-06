from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Expense
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, and_, or_

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    month_filter = request.args.get('month', '')
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')
    
    query = Expense.query.filter(Expense.user_id == current_user.id, Expense.is_deleted == False)
    
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            query = query.filter(
                func.strftime('%Y', Expense.date) == str(year),
                func.strftime('%m', Expense.date) == f"{month:02d}"
            )
        except:
            pass
    
    if category_filter:
        query = query.filter(Expense.category == category_filter)
    
    if search_query:
        query = query.filter(
            or_(
                Expense.category.contains(search_query),
                Expense.description.contains(search_query)
            )
        )
    
    pagination = query.order_by(Expense.date.desc()).paginate(page=page, per_page=20, error_out=False)
    expenses = pagination.items
    
    # Summary stats
    total_amount = db.session.query(func.sum(Expense.amount)).filter(
        Expense.user_id == current_user.id,
        Expense.is_deleted == False
    )
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            total_amount = total_amount.filter(
                func.strftime('%Y', Expense.date) == str(year),
                func.strftime('%m', Expense.date) == f"{month:02d}"
            )
        except:
            pass
    
    total_amount = total_amount.scalar() or Decimal('0')
    
    # Category-wise summary
    category_summary = db.session.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.user_id == current_user.id,
        Expense.is_deleted == False
    )
    
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            category_summary = category_summary.filter(
                func.strftime('%Y', Expense.date) == str(year),
                func.strftime('%m', Expense.date) == f"{month:02d}"
            )
        except:
            pass
    
    category_summary = category_summary.group_by(Expense.category).all()
    
    # Chart data
    chart_data = [
        {'category': c.category, 'total': float(c.total)} 
        for c in category_summary
    ]
    
    return render_template('admin/expenses/index.html',
                         expenses=expenses,
                         pagination=pagination,
                         total_amount=float(total_amount),
                         category_summary=category_summary,
                         chart_data=chart_data,
                         month_filter=month_filter,
                         category_filter=category_filter,
                         categories=Expense.EXPENSE_CATEGORIES)

@expenses_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        return create_expense_record()
    
    return render_template('admin/expenses/create.html', categories=Expense.EXPENSE_CATEGORIES)

def create_expense_record():
    try:
        category = request.form.get('category')
        description = request.form.get('description')
        amount = Decimal(request.form.get('amount'))
        date_str = request.form.get('date')
        
        if not category or not description or not amount or not date_str:
            flash('All fields are required', 'danger')
            return redirect(url_for('expenses.create'))
        
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return redirect(url_for('expenses.create'))
        
        expense = Expense(
            user_id=current_user.id,
            category=category,
            description=description,
            amount=amount,
            date=datetime.strptime(date_str, '%Y-%m-%d').date()
        )
        
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense record created successfully!', 'success')
        return redirect(url_for('expenses.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating record: {str(e)}', 'danger')
        return redirect(url_for('expenses.create'))

@expenses_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        try:
            expense.category = request.form.get('category')
            expense.description = request.form.get('description')
            expense.amount = Decimal(request.form.get('amount'))
            expense.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            expense.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Expense record updated successfully!', 'success')
            return redirect(url_for('expenses.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {str(e)}', 'danger')
    
    return render_template('admin/expenses/edit.html', expense=expense, categories=Expense.EXPENSE_CATEGORIES)

@expenses_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    expense = Expense.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        expense.is_deleted = True
        db.session.commit()
        flash('Expense record deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting record: {str(e)}', 'danger')
    
    return redirect(url_for('expenses.index'))
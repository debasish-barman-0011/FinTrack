from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Income
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, and_, or_

income_bp = Blueprint('income', __name__)

@income_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    month_filter = request.args.get('month', '')
    source_filter = request.args.get('source', '')
    search_query = request.args.get('search', '')
    
    query = Income.query.filter(Income.user_id == current_user.id, Income.is_deleted == False)
    
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            query = query.filter(
                func.strftime('%Y', Income.date) == str(year),
                func.strftime('%m', Income.date) == f"{month:02d}"
            )
        except:
            pass
    
    if source_filter:
        query = query.filter(Income.source == source_filter)
    
    if search_query:
        query = query.filter(
            or_(
                Income.source.contains(search_query),
                Income.remarks.contains(search_query)
            )
        )
    
    pagination = query.order_by(Income.date.desc()).paginate(page=page, per_page=20, error_out=False)
    incomes = pagination.items
    
    # Summary stats for current filtered view
    total_amount = db.session.query(func.sum(Income.amount)).filter(
        Income.user_id == current_user.id,
        Income.is_deleted == False
    )
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            total_amount = total_amount.filter(
                func.strftime('%Y', Income.date) == str(year),
                func.strftime('%m', Income.date) == f"{month:02d}"
            )
        except:
            pass
    
    total_amount = total_amount.scalar() or Decimal('0')
    
    # Source-wise summary
    source_summary = db.session.query(
        Income.source,
        func.sum(Income.amount).label('total')
    ).filter(
        Income.user_id == current_user.id,
        Income.is_deleted == False
    )
    
    if month_filter:
        try:
            year, month = map(int, month_filter.split('-'))
            source_summary = source_summary.filter(
                func.strftime('%Y', Income.date) == str(year),
                func.strftime('%m', Income.date) == f"{month:02d}"
            )
        except:
            pass
    
    source_summary = source_summary.group_by(Income.source).all()
    
    # Chart data
    chart_data = [
        {'source': s.source, 'total': float(s.total)} 
        for s in source_summary
    ]
    
    return render_template('admin/income/index.html',
                         incomes=incomes,
                         pagination=pagination,
                         total_amount=float(total_amount),
                         source_summary=source_summary,
                         chart_data=chart_data,
                         month_filter=month_filter,
                         source_filter=source_filter,
                         sources=Income.INCOME_SOURCES)

@income_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        return create_income_record()
    
    return render_template('admin/income/create.html', sources=Income.INCOME_SOURCES)

def create_income_record():
    try:
        source = request.form.get('source')
        amount = Decimal(request.form.get('amount'))
        remarks = request.form.get('remarks', '')
        date_str = request.form.get('date')
        
        if not source or not amount or not date_str:
            flash('All fields are required', 'danger')
            return redirect(url_for('income.create'))
        
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return redirect(url_for('income.create'))
        
        income = Income(
            user_id=current_user.id,
            source=source,
            amount=amount,
            remarks=remarks,
            date=datetime.strptime(date_str, '%Y-%m-%d').date()
        )
        
        db.session.add(income)
        db.session.commit()
        
        flash('Income record created successfully!', 'success')
        return redirect(url_for('income.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating record: {str(e)}', 'danger')
        return redirect(url_for('income.create'))

@income_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        try:
            income.source = request.form.get('source')
            income.amount = Decimal(request.form.get('amount'))
            income.remarks = request.form.get('remarks', '')
            income.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            income.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Income record updated successfully!', 'success')
            return redirect(url_for('income.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {str(e)}', 'danger')
    
    return render_template('admin/income/edit.html', income=income, sources=Income.INCOME_SOURCES)

@income_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    income = Income.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        income.is_deleted = True
        db.session.commit()
        flash('Income record deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting record: {str(e)}', 'danger')
    
    return redirect(url_for('income.index'))
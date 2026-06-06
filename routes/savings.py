from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Saving
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import func, and_, or_

savings_bp = Blueprint('savings', __name__)

@savings_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')
    show_recovered = request.args.get('show_recovered', 'false') == 'true'
    
    query = Saving.query.filter(Saving.user_id == current_user.id, Saving.is_deleted == False)
    
    if not show_recovered:
        query = query.filter(Saving.is_recovered == False)
    
    if category_filter:
        query = query.filter(Saving.category == category_filter)
    
    if search_query:
        query = query.filter(
            or_(
                Saving.category.contains(search_query),
                Saving.remarks.contains(search_query),
                Saving.sub_category.contains(search_query)
            )
        )
    
    pagination = query.order_by(Saving.date.desc()).paginate(page=page, per_page=20, error_out=False)
    savings = pagination.items
    
    # Category summary
    category_summary = db.session.query(
        Saving.category,
        func.sum(Saving.amount).label('total')
    ).filter(
        Saving.user_id == current_user.id,
        Saving.is_deleted == False,
        Saving.is_recovered == False
    )
    
    if category_filter:
        category_summary = category_summary.filter(Saving.category == category_filter)
    
    category_summary = category_summary.group_by(Saving.category).all()
    
    # Chart data
    chart_data = [
        {'category': c.category, 'total': float(c.total)} 
        for c in category_summary
    ]
    
    return render_template('admin/savings/index.html',
                         savings=savings,
                         pagination=pagination,
                         category_summary=category_summary,
                         chart_data=chart_data,
                         category_filter=category_filter,
                         show_recovered=show_recovered,
                         categories=Saving.SAVINGS_CATEGORIES,
                         investment_subcats=Saving.INVESTMENT_SUB_CATEGORIES)

@savings_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        return create_saving_record()
    
    return render_template('admin/savings/create.html', 
                         categories=Saving.SAVINGS_CATEGORIES,
                         investment_subcats=Saving.INVESTMENT_SUB_CATEGORIES)

def create_saving_record():
    try:
        category = request.form.get('category')
        sub_category = request.form.get('sub_category') if category == 'Investment' else None
        amount = Decimal(request.form.get('amount'))
        remarks = request.form.get('remarks')
        date_str = request.form.get('date')
        
        if not category or not amount or not remarks or not date_str:
            flash('All fields are required', 'danger')
            return redirect(url_for('savings.create'))
        
        if amount <= 0:
            flash('Amount must be greater than zero', 'danger')
            return redirect(url_for('savings.create'))
        
        saving = Saving(
            user_id=current_user.id,
            category=category,
            sub_category=sub_category,
            amount=amount,
            remarks=remarks,
            date=datetime.strptime(date_str, '%Y-%m-%d').date()
        )
        
        db.session.add(saving)
        db.session.commit()
        
        flash('Savings record created successfully!', 'success')
        return redirect(url_for('savings.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating record: {str(e)}', 'danger')
        return redirect(url_for('savings.create'))

@savings_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    saving = Saving.query.filter_by(id=id, user_id=current_user.id, is_deleted=False).first_or_404()
    
    if request.method == 'POST':
        try:
            saving.category = request.form.get('category')
            if saving.category == 'Investment':
                saving.sub_category = request.form.get('sub_category')
            else:
                saving.sub_category = None
            saving.amount = Decimal(request.form.get('amount'))
            saving.remarks = request.form.get('remarks')
            saving.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
            saving.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Savings record updated successfully!', 'success')
            return redirect(url_for('savings.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating record: {str(e)}', 'danger')
    
    return render_template('admin/savings/edit.html', 
                         saving=saving,
                         categories=Saving.SAVINGS_CATEGORIES,
                         investment_subcats=Saving.INVESTMENT_SUB_CATEGORIES)

@savings_bp.route('/recover/<int:id>', methods=['POST'])
@login_required
def recover(id):
    saving = Saving.query.filter_by(id=id, user_id=current_user.id, is_deleted=False).first_or_404()
    
    if saving.category != 'Borrowed to Others':
        flash('Only "Borrowed to Others" can be marked as recovered', 'danger')
        return redirect(url_for('savings.index'))
    
    try:
        saving.is_recovered = True
        saving.recovery_date = date.today()
        saving.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Amount of ₹{saving.amount} marked as recovered! It will be added back to your balance.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error recovering amount: {str(e)}', 'danger')
    
    return redirect(url_for('savings.index'))

@savings_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    saving = Saving.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    try:
        saving.is_deleted = True
        db.session.commit()
        flash('Savings record deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting record: {str(e)}', 'danger')
    
    return redirect(url_for('savings.index'))
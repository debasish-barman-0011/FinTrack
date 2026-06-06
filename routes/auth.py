from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            session.permanent = True
            
            # Check password expiry
            if user.is_password_expired():
                flash('Your password has expired. Please change your password.', 'warning')
                return redirect(url_for('auth.change_password'))
            
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('change_password.html')
        
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Your password has been changed successfully!', 'success')
        return redirect(url_for('dashboard.dashboard'))
    
    return render_template('change_password.html')
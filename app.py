from flask import Flask, render_template
from config import Config
from models import db
from flask_login import LoginManager
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.income import income_bp
    from routes.savings import savings_bp
    from routes.expenses import expenses_bp
    from routes.reports import reports_bp
    from routes.search import search_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/admin')
    app.register_blueprint(income_bp, url_prefix='/admin/income')
    app.register_blueprint(savings_bp, url_prefix='/admin/savings')
    app.register_blueprint(expenses_bp, url_prefix='/admin/expenses')
    app.register_blueprint(reports_bp, url_prefix='/admin/reports')
    app.register_blueprint(search_bp, url_prefix='/admin/search')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Public landing page
    @app.route('/')
    def landing():
        return render_template('landing.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
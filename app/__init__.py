import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Only try to create a directory for SQLite file-based DBs.
    # Render runs Postgres where the URI is not a filesystem path.
    uri = (app.config.get('SQLALCHEMY_DATABASE_URI') or '').strip()
    if uri.startswith('sqlite:///'):
        sqlite_path = uri.replace('sqlite:///', '', 1)
        if sqlite_path and sqlite_path != ':memory:':
            sqlite_dir = os.path.dirname(sqlite_path)
            if sqlite_dir:
                os.makedirs(sqlite_dir, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)

    # Render's Python runtime sets `GUNICORN_CMD_ARGS=--preload ...` by default.
    # With preload, app code runs in a master process before fork; opening DB
    # connections there can cause slow startups and broken pooled connections
    # in workers. So we avoid automatic DB init on Render/Postgres by default.
    #
    # If you need to initialize/seed the production DB once, set `AUTO_DB_INIT=1`
    # temporarily on Render and redeploy.
    auto_db_init = os.environ.get('AUTO_DB_INIT', '').strip().lower() in {'1', 'true', 'yes'}
    is_sqlite = uri.startswith('sqlite:///')
    is_render = os.environ.get('RENDER', '').strip().lower() == 'true'
    if is_sqlite or auto_db_init or not is_render:
        with app.app_context():
            db.create_all()
            _seed_data()

    # If Gunicorn preloads the app then forks workers, dispose inherited pools
    # in the child so each worker creates its own fresh DB connections.
    if hasattr(os, 'register_at_fork'):
        def _after_fork_child():
            try:
                with app.app_context():
                    db.session.remove()
                    # Don't close parent's connections; just replace the pool.
                    db.engine.dispose(close=False)
            except Exception:
                # Avoid crashing worker startup on best-effort cleanup.
                pass

        try:
            os.register_at_fork(after_in_child=_after_fork_child)
        except Exception:
            pass

    # Context processor for templates
    @app.context_processor
    def inject_globals():
        return {
            'brand_name': app.config['BRAND_NAME'],
            'brand_year': app.config['BRAND_YEAR'],
            'whatsapp_number': app.config['WHATSAPP_NUMBER'],
        }

    return app


def _seed_data():
    """Seed initial categories if empty."""
    from app.models import Category, User

    if Category.query.first() is None:
        categories = [
            Category(name='زفات وأفراح', slug='zaffat', description='زفات عرس مميزة لإضفاء لمسة خاصة على ليلة العمر', icon='fas fa-ring', sort_order=1),
            Category(name='مناسبات اجتماعية', slug='social', description='أعمال صوتية لحفلات التخرج والخطوبة والنجاح', icon='fas fa-graduation-cap', sort_order=2),
            Category(name='مواليد وأطفال', slug='newborn', description='أناشيد وأعمال ترحيبية بالمواليد الجدد', icon='fas fa-baby', sort_order=3),
            Category(name='أعياد ومناسبات شخصية', slug='celebrations', description='أعمال صوتية مخصصة للأعياد والمناسبات الخاصة', icon='fas fa-gift', sort_order=4),
            Category(name='شيلات مخصصة', slug='sheilat', description='شيلات حماسية مخصصة بالأسماء والتفاصيل', icon='fas fa-music', sort_order=5),
        ]
        db.session.add_all(categories)
        db.session.commit()

    # Create default admin if no users
    if User.query.first() is None:
        admin = User(
            name='مدير النظام',
            email='admin@sumo.sa',
            phone='+966500000000',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

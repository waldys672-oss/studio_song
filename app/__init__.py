import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')), ''), exist_ok=True)

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

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        _seed_data()

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
            Category(name='زفات وأفراح', slug='zaffat', description='زفات عرس مميزة لإضفاء لمسة خاصة على ليلة العمر', icon='💍', sort_order=1),
            Category(name='مناسبات اجتماعية', slug='social', description='أعمال صوتية لحفلات التخرج والخطوبة والنجاح', icon='🎓', sort_order=2),
            Category(name='مواليد وأطفال', slug='newborn', description='أناشيد وأعمال ترحيبية بالمواليد الجدد', icon='👶', sort_order=3),
            Category(name='أعياد ومناسبات شخصية', slug='celebrations', description='أعمال صوتية مخصصة للأعياد والمناسبات الخاصة', icon='🎉', sort_order=4),
            Category(name='شيلات مخصصة', slug='sheilat', description='شيلات حماسية مخصصة بالأسماء والتفاصيل', icon='🎵', sort_order=5),
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

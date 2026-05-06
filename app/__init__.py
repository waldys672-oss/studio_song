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
        from app.models import Category

        return {
            'brand_name': app.config['BRAND_NAME'],
            'brand_year': app.config['BRAND_YEAR'],
            'whatsapp_number': app.config['WHATSAPP_NUMBER'],
            'footer_categories': Category.query.filter_by(parent_id=None).order_by(Category.sort_order).limit(5).all(),
        }

    return app


def _seed_data():
    """Seed initial categories and subcategories (idempotent — safe to run repeatedly)."""
    from app.models import Category, User

    if Category.query.count() > 0:
        if User.query.first() is None:
            admin = User(
                name='مدير النظام',
                email='admin@sumo.sa',
                phone='+966558262881',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
        return

    # ── Helper: get or create a category by slug ──────────────────────────────
    def _upsert_category(**kwargs):
        slug = kwargs['slug']
        cat = Category.query.filter_by(slug=slug).first()
        if cat is None:
            cat = Category(**kwargs)
            db.session.add(cat)
        return cat

    # ── 0. Fix slug mismatch: production has 'social', we now want 'success' ─
    #    Rename the existing row so the upsert below finds it correctly.
    old_social = Category.query.filter_by(slug='social').first()
    if old_social:
        old_social.slug = 'success'
        old_social.name = 'نجاح وتخرج'

    # Also clean up orphan 'success' row if one was already created by previous deploy
    db.session.flush()
    dupes = Category.query.filter_by(slug='success', parent_id=None).all()
    if len(dupes) > 1:
        # Keep the one with the lowest id (original), delete extras
        dupes.sort(key=lambda c: c.id)
        for orphan in dupes[1:]:
            # Re-parent any subcategories that point to the orphan
            for sub in Category.query.filter_by(parent_id=orphan.id).all():
                sub.parent_id = dupes[0].id
            db.session.delete(orphan)
        db.session.flush()

    # ── 1. Main categories ────────────────────────────────────────────────────
    zaffat       = _upsert_category(name='زفات وأفراح',           slug='zaffat',       description='زفات عرس مميزة لإضفاء لمسة خاصة على ليلة العمر',            icon='fas fa-ring',           sort_order=1)
    success      = _upsert_category(name='نجاح وتخرج',            slug='success',      description='أعمال صوتية لحفلات التخرج والخطوبة والنجاح',                icon='fas fa-graduation-cap', sort_order=2)
    newborn      = _upsert_category(name='مواليد وأطفال',         slug='newborn',      description='أناشيد وأعمال ترحيبية بالمواليد الجدد',                      icon='fas fa-baby',           sort_order=3)
    celebrations = _upsert_category(name='أعياد ومناسبات شخصية', slug='celebrations', description='أعمال صوتية مخصصة للأعياد والمناسبات الخاصة',               icon='fas fa-gift',           sort_order=4)
    sheilat      = _upsert_category(name='شيلات مخصصة',           slug='sheilat',      description='شيلات حماسية مخصصة بالأسماء والتفاصيل',                     icon='fas fa-music',          sort_order=5)
    db.session.flush()   # assigns IDs so parent_id references work below

    # ── 2. Subcategories: زفات وأفراح ─────────────────────────────────────────
    _upsert_category(name='زفات دخول العروس',        slug='entrance-zaffat',      description='زفات خاصة لتنظيم دخول العروس للقاعة بأسلوب مميز',         icon='fas fa-door-open',      sort_order=1, parent_id=zaffat.id)
    _upsert_category(name='زفات ملكية فاخرة',         slug='royal-zaffat',         description='زفة فخمة بتنسيق موسيقي ملكي فاخر',                         icon='fas fa-crown',          sort_order=2, parent_id=zaffat.id)
    _upsert_category(name='زفات المسار والكوشة',      slug='walkway-zaffat',       description='مخصصة للمشي على الممشى وصولاً إلى المنصة',                  icon='fas fa-route',          sort_order=3, parent_id=zaffat.id)
    _upsert_category(name='زفات وداع للعروسة',        slug='farewell-zaffat',      description='زفات وداع العروسة لبيت أهلها بأجمل اللحظات',               icon='fas fa-heart-broken',   sort_order=4, parent_id=zaffat.id)
    _upsert_category(name='زفة خطوبة',                slug='rings-zaffat',         description='موسيقى خاصة لتبادل الخواتم وأجمل لحظات الخطوبة',           icon='fas fa-ring',           sort_order=5, parent_id=zaffat.id)
    _upsert_category(name='زفات عقد قران',             slug='royal-zaffat-ncm',     description='زفات خاصة لحفل عقد القران والتوقيع',                       icon='fas fa-crown',          sort_order=6, parent_id=zaffat.id)
    _upsert_category(name='زفات باسم العائلة',        slug='family-name-zaffat',   description='زفات مخصصة تحمل اسم العائلة وتفاصيلها',                    icon='fas fa-users',          sort_order=7, parent_id=zaffat.id)
    _upsert_category(name='زفات باسم العروسين',       slug='couple-name-zaffat',   description='زفات مخصصة باسم العريس والعروس',                           icon='fas fa-ring',           sort_order=8, parent_id=zaffat.id)
    _upsert_category(name='زفات للأم (العريس/العروس)',slug='mothers-zaffat',       description='زفات مهداة للأم في ليلة الفرح',                             icon='fas fa-heart',          sort_order=9, parent_id=zaffat.id)

    # ── 3. Subcategories: نجاح وتخرج ──────────────────────────────────────────
    _upsert_category(name='تخرج البنات',    slug='girls-graduation',      description='زفات تخرج مخصصة للطالبات',                      icon='fas fa-graduation-cap', sort_order=1, parent_id=success.id)
    _upsert_category(name='تخرج الأولاد',   slug='boys-graduation',       description='زفات تخرج مخصصة للطلاب',                        icon='fas fa-graduation-cap', sort_order=2, parent_id=success.id)
    _upsert_category(name='تخرج جامعي',     slug='university-graduation', description='زفات تخرج جامعي احتفالية رائعة',                 icon='fas fa-university',     sort_order=3, parent_id=success.id)

    # ── 4. Subcategories: مواليد وأطفال ───────────────────────────────────────
    _upsert_category(name='مواليد جدد',    slug='babies',      description='أناشيد ترحيبية بالمولود الجديد',     icon='fas fa-baby',       sort_order=1, parent_id=newborn.id)
    _upsert_category(name='أعياد ميلاد أطفال', slug='kids-birthday', description='أغاني وأعمال خاصة بأعياد ميلاد الأطفال', icon='fas fa-birthday-cake', sort_order=2, parent_id=newborn.id)

    # ── 5. Subcategories: أعياد ومناسبات شخصية ────────────────────────────────
    _upsert_category(name='أعياد ميلاد',    slug='birthdays',      description='أعمال صوتية مخصصة لأعياد الميلاد',             icon='fas fa-birthday-cake', sort_order=1, parent_id=celebrations.id)
    _upsert_category(name='مناسبات خاصة',  slug='special-occasions', description='أعمال لكل مناسبة خاصة وفريدة',             icon='fas fa-star',          sort_order=2, parent_id=celebrations.id)

    # ── 6. Subcategories: شيلات مخصصة ─────────────────────────────────────────
    # Repair broken slugs that may already exist in production
    _SLUG_REPAIRS = {
        'sang':       ('sheilat-atabah', 'شيلات عتاب',  'fas fa-comment-dots', 1),
        'fffffffd':   ('sheilat-hamasa', 'شيلات حماسة', 'fas fa-fire',         4),
        'rrrfrdcfd':  ('sheilat-fakhr',  'شيلات فخر',   'fas fa-medal',        5),
    }
    for bad_slug, (good_slug, good_name, good_icon, good_order) in _SLUG_REPAIRS.items():
        broken = Category.query.filter_by(slug=bad_slug).first()
        if broken:
            broken.slug       = good_slug
            broken.name       = good_name
            broken.icon       = good_icon
            broken.sort_order = good_order
            broken.parent_id  = sheilat.id
    # Handle the duplicate 'rrrfffd' case (two rows with same bad slug)
    broken_dupes = Category.query.filter_by(slug='rrrfffd').all()
    target_slugs = [('sheilat-ruh', 'شيلات روح', 'fas fa-feather-alt', 2),
                    ('sheilat-faraq', 'شيلات فراق', 'fas fa-heart-broken', 3)]
    for i, row in enumerate(broken_dupes[:2]):
        row.slug, row.name, row.icon, row.sort_order = target_slugs[i]
        row.parent_id = sheilat.id
    db.session.flush()

    _upsert_category(name='شيلات عتاب',  slug='sheilat-atabah',  description='شيلات عتاب رقيقة بأسلوب عاطفي مؤثر',        icon='fas fa-comment-dots', sort_order=1, parent_id=sheilat.id)
    _upsert_category(name='شيلات روح',   slug='sheilat-ruh',     description='شيلات روحانية هادئة بأسلوب راقٍ',            icon='fas fa-feather-alt',  sort_order=2, parent_id=sheilat.id)
    _upsert_category(name='شيلات فراق',  slug='sheilat-faraq',   description='شيلات فراق وتوديع بكلمات معبّرة',            icon='fas fa-heart-broken', sort_order=3, parent_id=sheilat.id)
    _upsert_category(name='شيلات حماسة', slug='sheilat-hamasa',  description='شيلات حماسية تُشعل الحفلات والمناسبات',       icon='fas fa-fire',         sort_order=4, parent_id=sheilat.id)
    _upsert_category(name='شيلات فخر',   slug='sheilat-fakhr',   description='شيلات فخر وانتماء بصوت يحرّك المشاعر',        icon='fas fa-medal',        sort_order=5, parent_id=sheilat.id)

    db.session.commit()

    # ── 7. Default admin ───────────────────────────────────────────────────────
    if User.query.first() is None:
        admin = User(
            name='مدير النظام',
            email='admin@sumo.sa',
            phone='+966558262881',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

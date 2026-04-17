from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    samples = db.relationship('Sample', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


class Sample(db.Model):
    __tablename__ = 'samples'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    media_type = db.Column(db.String(20), nullable=False, default='youtube')  # youtube | upload
    media_url = db.Column(db.String(500), nullable=False)  # YouTube URL or uploaded file path
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def get_youtube_embed_id(self):
        """Extract YouTube video ID from URL for embedding."""
        url = self.media_url
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[-1].split('?')[0]
        if 'youtube.com/watch' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            return params.get('v', [''])[0]
        if 'youtube.com/embed/' in url:
            return url.split('embed/')[-1].split('?')[0]
        return url

    def __repr__(self):
        return f'<Sample {self.title}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for guests
    guest_name = db.Column(db.String(100), nullable=True)
    guest_phone = db.Column(db.String(20), nullable=True)
    names_requested = db.Column(db.String(300), nullable=False)
    occasion_type = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(50), nullable=False)  # زفة | شيلة | مقطع
    reference_sample_id = db.Column(db.Integer, db.ForeignKey('samples.id'), nullable=True)
    details = db.Column(db.Text, nullable=True)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='new')  # new | in_progress | delivered
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    reference_sample = db.relationship('Sample', backref='orders')
    tracking_updates = db.relationship('TrackingUpdate', backref='order',
                                       lazy='dynamic', order_by='TrackingUpdate.created_at.desc()')

    @property
    def status_label(self):
        labels = {
            'new': 'جديد',
            'in_progress': 'قيد التنفيذ',
            'delivered': 'تم التسليم'
        }
        return labels.get(self.status, self.status)

    @property
    def status_color(self):
        colors = {
            'new': 'info',
            'in_progress': 'warning',
            'delivered': 'success'
        }
        return colors.get(self.status, 'info')

    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'


class TrackingUpdate(db.Model):
    __tablename__ = 'tracking_updates'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def status_label(self):
        labels = {
            'new': 'جديد',
            'in_progress': 'قيد التنفيذ',
            'delivered': 'تم التسليم'
        }
        return labels.get(self.status, self.status)

    def __repr__(self):
        return f'<TrackingUpdate {self.order_id} - {self.status}>'

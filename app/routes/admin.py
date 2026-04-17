import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Sample, Category, Order, TrackingUpdate, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'webm', 'ogg', 'm4a'}


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('ليس لديك صلاحية الوصول', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/')
@admin_required
def dashboard():
    total_samples = Sample.query.count()
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    in_progress = Order.query.filter_by(status='in_progress').count()
    delivered = Order.query.filter_by(status='delivered').count()
    total_users = User.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_samples=total_samples,
                           total_orders=total_orders,
                           new_orders=new_orders,
                           in_progress=in_progress,
                           delivered=delivered,
                           total_users=total_users,
                           recent_orders=recent_orders)


# ─── Samples Management ───

@admin_bp.route('/samples')
@admin_required
def samples():
    all_samples = Sample.query.order_by(Sample.created_at.desc()).all()
    return render_template('admin/samples.html', samples=all_samples)


@admin_bp.route('/samples/add', methods=['GET', 'POST'])
@admin_required
def add_sample():
    categories = Category.query.order_by(Category.sort_order).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        media_type = request.form.get('media_type', 'youtube')
        is_featured = request.form.get('is_featured') == 'on'
        media_url = ''

        if media_type == 'youtube':
            media_url = request.form.get('youtube_url', '').strip()
            if not media_url:
                flash('رابط YouTube مطلوب', 'error')
                return render_template('admin/sample_form.html', categories=categories)
        else:
            file = request.files.get('media_file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid collisions
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                media_url = filename
            else:
                flash('الملف غير صالح أو مفقود', 'error')
                return render_template('admin/sample_form.html', categories=categories)

        if not title or not category_id:
            flash('العنوان والقسم مطلوبان', 'error')
            return render_template('admin/sample_form.html', categories=categories)

        sample = Sample(
            title=title,
            category_id=category_id,
            media_type=media_type,
            media_url=media_url,
            is_featured=is_featured
        )
        db.session.add(sample)
        db.session.commit()
        flash('تم إضافة العمل بنجاح', 'success')
        return redirect(url_for('admin.samples'))

    return render_template('admin/sample_form.html', categories=categories, sample=None)


@admin_bp.route('/samples/<int:sample_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_sample(sample_id):
    sample = db.session.get(Sample, sample_id)
    if not sample:
        flash('العمل غير موجود', 'error')
        return redirect(url_for('admin.samples'))

    categories = Category.query.order_by(Category.sort_order).all()

    if request.method == 'POST':
        sample.title = request.form.get('title', '').strip()
        sample.category_id = request.form.get('category_id', type=int)
        sample.is_featured = request.form.get('is_featured') == 'on'
        media_type = request.form.get('media_type', 'youtube')

        if media_type == 'youtube':
            sample.media_type = 'youtube'
            sample.media_url = request.form.get('youtube_url', '').strip()
        elif request.files.get('media_file'):
            file = request.files['media_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                sample.media_type = 'upload'
                sample.media_url = filename

        db.session.commit()
        flash('تم تحديث العمل بنجاح', 'success')
        return redirect(url_for('admin.samples'))

    return render_template('admin/sample_form.html', categories=categories, sample=sample)


@admin_bp.route('/samples/<int:sample_id>/delete', methods=['POST'])
@admin_required
def delete_sample(sample_id):
    sample = db.session.get(Sample, sample_id)
    if sample:
        # Delete uploaded file if exists
        if sample.media_type == 'upload' and sample.media_url:
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], sample.media_url)
            if os.path.exists(filepath):
                os.remove(filepath)
        db.session.delete(sample)
        db.session.commit()
        flash('تم حذف العمل', 'success')
    return redirect(url_for('admin.samples'))


# ─── Orders Management ───

@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status', '')
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    all_orders = query.all()
    return render_template('admin/orders.html', orders=all_orders, status_filter=status_filter)


@admin_bp.route('/orders/<int:order_id>', methods=['GET', 'POST'])
@admin_required
def order_detail(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        flash('الطلب غير موجود', 'error')
        return redirect(url_for('admin.orders'))

    if request.method == 'POST':
        new_status = request.form.get('status', '')
        note = request.form.get('note', '').strip()

        if new_status and new_status != order.status:
            order.status = new_status
            tracking = TrackingUpdate(
                order_id=order.id,
                status=new_status,
                note=note or f'تم تحديث الحالة إلى: {order.status_label}'
            )
            db.session.add(tracking)
            db.session.commit()
            flash('تم تحديث حالة الطلب', 'success')

    tracking = order.tracking_updates.order_by(TrackingUpdate.created_at.asc()).all()
    return render_template('admin/order_detail.html', order=order, tracking=tracking)

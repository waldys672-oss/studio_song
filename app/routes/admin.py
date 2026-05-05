import os
import time

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Sample, Category, Order, TrackingUpdate, User
import cloudinary.uploader


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# أضف صيغ الصور هنا
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'webm', 'ogg', 'm4a', 'jpg', 'jpeg', 'png', 'webp'}


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


def save_file(file):
    """Helper to save uploaded media to Cloudinary (with local fallback)."""
    if file and file.filename and allowed_file(file.filename):
        # Upload to Cloudinary first when configured.
        if current_app.config.get('CLOUDINARY_URL'):
            try:
                upload_result = cloudinary.uploader.upload(file, resource_type="auto")
                secure_url = upload_result.get('secure_url')
                if secure_url:
                    return secure_url
            except Exception as e:
                current_app.logger.warning(f"Cloudinary upload failed, falling back to local storage: {e}")
                try:
                    file.stream.seek(0)
                except Exception:
                    pass

        # Fallback to local static/uploads storage.
        filename = secure_filename(file.filename)
        if not filename:
            return None
        unique_filename = f"{int(time.time() * 1000)}_{filename}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(save_path)
        return unique_filename
    return None


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
        cover_image = None

        if media_type == 'youtube':
            media_url = request.form.get('youtube_url', '').strip()
        else:
            # حفظ ملف الميديا (صوت أو فيديو)
            media_url = save_file(request.files.get('media_file'))
            # حفظ صورة الغلاف
            cover_image = save_file(request.files.get('cover_image'))

        if not title or not media_url:
            flash('العنوان والملف/الرابط مطلوبان', 'error')
            return redirect(request.url)

        sample = Sample(
            title=title,
            category_id=category_id,
            media_type=media_type,
            media_url=media_url,
            cover_image=cover_image, # حفظ الصورة
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
    categories = Category.query.order_by(Category.sort_order).all()
    
    if request.method == 'POST':
        sample.title = request.form.get('title', '').strip()
        sample.category_id = request.form.get('category_id', type=int)
        sample.is_featured = request.form.get('is_featured') == 'on'
        media_type = request.form.get('media_type', 'youtube')

        if media_type == 'youtube':
            sample.media_type = 'youtube'
            sample.media_url = request.form.get('youtube_url', '').strip()
        else:
            # تحديث ملف الميديا إذا رفع المستخدم ملفاً جديداً
            new_media = save_file(request.files.get('media_file'))
            if new_media:
                sample.media_url = new_media
                sample.media_type = 'upload'
            
            # تحديث صورة الغلاف إذا رفع المستخدم واحدة جديدة
            new_cover = save_file(request.files.get('cover_image'))
            if new_cover:
                sample.cover_image = new_cover

        db.session.commit()
        flash('تم تحديث العمل بنجاح', 'success')
        return redirect(url_for('admin.samples'))

    return render_template('admin/sample_form.html', categories=categories, sample=sample)

@admin_bp.route('/samples/<int:sample_id>/delete', methods=['POST'])
@admin_required
def delete_sample(sample_id):
    sample = db.session.get(Sample, sample_id)
    if sample:
        # حذف الملفات من السيرفر لتوفير المساحة
        for filename in [sample.media_url, sample.cover_image]:
            if filename and sample.media_type == 'upload' and not str(filename).startswith(('http://', 'https://')):
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        
        db.session.delete(sample)
        db.session.commit()
        flash('تم حذف العمل', 'success')
    return redirect(url_for('admin.samples'))


# ─── Categories Management ───

def _slugify(text):
    """Simple ASCII slug generator."""
    import re, unicodedata
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[\s_-]+', '-', text)


@admin_bp.route('/categories')
@admin_required
def categories():
    all_cats = Category.query.order_by(
        Category.parent_id.asc(), Category.sort_order.asc()
    ).all()
    return render_template('admin/categories.html', categories=all_cats)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    parent_options = Category.query.filter_by(parent_id=None).order_by(Category.sort_order).all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = request.form.get('slug', '').strip() or _slugify(name)
        description = request.form.get('description', '').strip()
        icon = request.form.get('icon', '').strip()
        sort_order = request.form.get('sort_order', 0, type=int)
        parent_id = request.form.get('parent_id', type=int) or None

        if not name or not slug:
            flash('الاسم والـ Slug مطلوبان', 'error')
            return redirect(request.url)

        if Category.query.filter_by(slug=slug).first():
            flash('هذا الـ Slug مستخدم بالفعل، اختر آخر', 'error')
            return redirect(request.url)

        cat = Category(name=name, slug=slug, description=description,
                       icon=icon, sort_order=sort_order, parent_id=parent_id)
        db.session.add(cat)
        db.session.commit()
        flash(f'تم إضافة القسم «{name}» بنجاح', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=None,
                           parent_options=parent_options)


@admin_bp.route('/categories/<int:cat_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        flash('القسم غير موجود', 'error')
        return redirect(url_for('admin.categories'))

    parent_options = Category.query.filter(
        Category.parent_id == None,
        Category.id != cat_id
    ).order_by(Category.sort_order).all()

    if request.method == 'POST':
        cat.name = request.form.get('name', '').strip()
        cat.slug = request.form.get('slug', '').strip() or _slugify(cat.name)
        cat.description = request.form.get('description', '').strip()
        cat.icon = request.form.get('icon', '').strip()
        cat.sort_order = request.form.get('sort_order', 0, type=int)
        cat.parent_id = request.form.get('parent_id', type=int) or None

        existing = Category.query.filter_by(slug=cat.slug).first()
        if existing and existing.id != cat_id:
            flash('هذا الـ Slug مستخدم بالفعل، اختر آخر', 'error')
            return redirect(request.url)

        db.session.commit()
        flash(f'تم تحديث القسم «{cat.name}» بنجاح', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=cat,
                           parent_options=parent_options)


@admin_bp.route('/categories/<int:cat_id>/delete', methods=['POST'])
@admin_required
def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        flash('القسم غير موجود', 'error')
        return redirect(url_for('admin.categories'))

    if cat.samples.count() > 0:
        flash(f'لا يمكن حذف «{cat.name}» لأنه يحتوي على {cat.samples.count()} عمل. احذف الأعمال أولاً.', 'error')
        return redirect(url_for('admin.categories'))

    if cat.subcategories.count() > 0:
        flash(f'لا يمكن حذف «{cat.name}» لأنه يحتوي على أقسام فرعية. احذفها أولاً.', 'error')
        return redirect(url_for('admin.categories'))

    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    flash(f'تم حذف القسم «{name}»', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/samples')
@admin_required
def samples():
    """دالة عرض جميع الأعمال في لوحة التحكم"""
    all_samples = Sample.query.order_by(Sample.created_at.desc()).all()
    return render_template('admin/samples.html', samples=all_samples)
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

import os
import re
import time

from functools import wraps

import cloudinary.uploader
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload, selectinload
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Category, Order, Sample, Singer, TrackingUpdate, User


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'webm', 'ogg', 'm4a', 'jpg', 'jpeg', 'png', 'webp'}
IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('ليس لديك صلاحية الوصول', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename, extensions=ALLOWED_EXTENSIONS):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


def file_has_invalid_extension(file, extensions):
    return bool(file and file.filename and not allowed_file(file.filename, extensions))


def normalize_slug(value):
    value = re.sub(r'[^\w\s-]', '', (value or '').strip().lower(), flags=re.UNICODE)
    return re.sub(r'[-\s]+', '-', value, flags=re.UNICODE).strip('-_')


def get_parent_categories(exclude_id=None):
    query = Category.query.filter_by(parent_id=None)
    if exclude_id is not None:
        query = query.filter(Category.id != exclude_id)
    return query.order_by(Category.sort_order, Category.name).all()


def get_sample_categories():
    return Category.query.order_by(Category.parent_id, Category.sort_order, Category.name).all()


def get_singers():
    return Singer.query.order_by(Singer.sort_order, Singer.name).all()


def parse_category_form(category=None):
    name = request.form.get('name', '').strip()
    raw_slug = request.form.get('slug', '').strip()
    slug = normalize_slug(raw_slug or name)
    description = request.form.get('description', '').strip() or None
    icon = request.form.get('icon', '').strip() or 'fas fa-folder'
    sort_order = request.form.get('sort_order', type=int)
    parent_id = request.form.get('parent_id', type=int)

    if sort_order is None:
        sort_order = 0
    if not parent_id:
        parent_id = None

    errors = []
    if not name:
        errors.append('اسم القسم مطلوب')
    if not slug:
        errors.append('الرابط المختصر مطلوب')
    else:
        slug_query = Category.query.filter_by(slug=slug)
        if category is not None:
            slug_query = slug_query.filter(Category.id != category.id)
        if slug_query.first():
            errors.append('الرابط المختصر مستخدم بالفعل')

    if parent_id is not None:
        parent = db.session.get(Category, parent_id)
        if parent is None:
            errors.append('القسم الأب غير موجود')
        elif parent.parent_id is not None:
            errors.append('يمكن اختيار قسم رئيسي فقط كقسم أب')
        elif category is not None and parent.id == category.id:
            errors.append('لا يمكن اختيار نفس القسم كقسم أب')
        elif category is not None and category.subcategories.count() > 0:
            errors.append('لا يمكن تحويل قسم رئيسي لديه أقسام فرعية إلى قسم فرعي')

    return {
        'name': name,
        'slug': slug,
        'description': description,
        'icon': icon,
        'sort_order': sort_order,
        'parent_id': parent_id,
    }, errors


def parse_singer_form(singer=None):
    name = request.form.get('name', '').strip()
    raw_slug = request.form.get('slug', '').strip()
    slug = normalize_slug(raw_slug or name)
    sort_order = request.form.get('sort_order', type=int)

    if sort_order is None:
        sort_order = 0

    errors = []
    if not name:
        errors.append('اسم الفنان مطلوب')
    if not slug:
        errors.append('الرابط المختصر مطلوب')
    else:
        slug_query = Singer.query.filter_by(slug=slug)
        if singer is not None:
            slug_query = slug_query.filter(Singer.id != singer.id)
        if slug_query.first():
            errors.append('الرابط المختصر مستخدم بالفعل')

    return {
        'name': name,
        'slug': slug,
        'sort_order': sort_order,
    }, errors


def get_selected_singers():
    singer_ids = []
    for raw_id in request.form.getlist('singer_ids'):
        try:
            singer_ids.append(int(raw_id))
        except (TypeError, ValueError):
            continue

    if not singer_ids:
        return [], ['اختر فناناً واحداً على الأقل']

    singers = Singer.query.filter(Singer.id.in_(singer_ids)).all()
    if len(singers) != len(set(singer_ids)):
        return singers, ['يوجد فنان غير صالح في الاختيار']

    return singers, []


def save_file(file, extensions=ALLOWED_EXTENSIONS, resource_type='auto'):
    if file and file.filename and allowed_file(file.filename, extensions):
        if current_app.config.get('CLOUDINARY_URL'):
            try:
                upload_result = cloudinary.uploader.upload(file, resource_type=resource_type)
                secure_url = upload_result.get('secure_url')
                if secure_url:
                    return secure_url
            except Exception as exc:
                current_app.logger.warning(f'Cloudinary upload failed, falling back to local storage: {exc}')
                try:
                    file.stream.seek(0)
                except Exception:
                    pass

        filename = secure_filename(file.filename)
        if not filename:
            return None
        unique_filename = f'{int(time.time() * 1000)}_{filename}'
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(save_path)
        return unique_filename
    return None


@admin_bp.route('/')
@admin_required
def dashboard():
    total_samples = Sample.query.count()
    total_categories = Category.query.count()
    total_singers = Singer.query.count()
    total_orders = Order.query.count()
    new_orders = Order.query.filter_by(status='new').count()
    in_progress = Order.query.filter_by(status='in_progress').count()
    delivered = Order.query.filter_by(status='delivered').count()
    total_users = User.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_samples=total_samples,
        total_categories=total_categories,
        total_singers=total_singers,
        total_orders=total_orders,
        new_orders=new_orders,
        in_progress=in_progress,
        delivered=delivered,
        total_users=total_users,
        recent_orders=recent_orders,
    )


@admin_bp.route('/categories')
@admin_required
def categories():
    all_categories = Category.query.order_by(Category.parent_id, Category.sort_order, Category.name).all()
    return render_template('admin/categories.html', categories=all_categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    parent_categories = get_parent_categories()

    if request.method == 'POST':
        form_data, errors = parse_category_form()
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/category_form.html', category=None, parent_categories=parent_categories)

        category = Category(**form_data)
        db.session.add(category)
        db.session.commit()
        flash('تمت إضافة القسم بنجاح', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=None, parent_categories=parent_categories)


@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        flash('القسم غير موجود', 'error')
        return redirect(url_for('admin.categories'))

    parent_categories = get_parent_categories(exclude_id=category.id)

    if request.method == 'POST':
        form_data, errors = parse_category_form(category=category)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template(
                'admin/category_form.html',
                category=category,
                parent_categories=parent_categories,
            )

        category.name = form_data['name']
        category.slug = form_data['slug']
        category.description = form_data['description']
        category.icon = form_data['icon']
        category.sort_order = form_data['sort_order']
        category.parent_id = form_data['parent_id']
        db.session.commit()
        flash('تم تحديث القسم بنجاح', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/category_form.html', category=category, parent_categories=parent_categories)


@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        flash('القسم غير موجود', 'error')
        return redirect(url_for('admin.categories'))

    if category.subcategories.count() > 0:
        flash('لا يمكن حذف قسم يحتوي على أقسام فرعية', 'error')
        return redirect(url_for('admin.categories'))

    if category.samples.count() > 0:
        flash('لا يمكن حذف قسم مرتبط بأعمال موجودة', 'error')
        return redirect(url_for('admin.categories'))

    if Order.query.filter_by(subcategory_id=category.id).first():
        flash('لا يمكن حذف قسم مرتبط بطلبات موجودة', 'error')
        return redirect(url_for('admin.categories'))

    db.session.delete(category)
    db.session.commit()
    flash('تم حذف القسم', 'success')
    return redirect(url_for('admin.categories'))


@admin_bp.route('/singers')
@admin_required
def singers():
    all_singers = get_singers()
    return render_template('admin/singers.html', singers=all_singers)


@admin_bp.route('/singers/add', methods=['GET', 'POST'])
@admin_required
def add_singer():
    if request.method == 'POST':
        form_data, errors = parse_singer_form()
        background_file = request.files.get('background_image')
        if file_has_invalid_extension(background_file, IMAGE_EXTENSIONS):
            errors.append('صيغة صورة الخلفية غير مدعومة')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/singer_form.html', singer=None)

        background_image = save_file(
            background_file,
            extensions=IMAGE_EXTENSIONS,
            resource_type='image',
        )
        singer = Singer(**form_data, background_image=background_image)
        db.session.add(singer)
        db.session.commit()
        flash('تمت إضافة الفنان بنجاح', 'success')
        return redirect(url_for('admin.singers'))

    return render_template('admin/singer_form.html', singer=None)


@admin_bp.route('/singers/<int:singer_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_singer(singer_id):
    singer = db.session.get(Singer, singer_id)
    if not singer:
        flash('الفنان غير موجود', 'error')
        return redirect(url_for('admin.singers'))

    if request.method == 'POST':
        form_data, errors = parse_singer_form(singer=singer)
        background_file = request.files.get('background_image')
        if file_has_invalid_extension(background_file, IMAGE_EXTENSIONS):
            errors.append('صيغة صورة الخلفية غير مدعومة')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/singer_form.html', singer=singer)

        new_background = save_file(
            background_file,
            extensions=IMAGE_EXTENSIONS,
            resource_type='image',
        )
        singer.name = form_data['name']
        singer.slug = form_data['slug']
        singer.sort_order = form_data['sort_order']
        if new_background:
            singer.background_image = new_background

        db.session.commit()
        flash('تم تحديث الفنان بنجاح', 'success')
        return redirect(url_for('admin.singers'))

    return render_template('admin/singer_form.html', singer=singer)


@admin_bp.route('/singers/<int:singer_id>/delete', methods=['POST'])
@admin_required
def delete_singer(singer_id):
    singer = db.session.get(Singer, singer_id)
    if not singer:
        flash('الفنان غير موجود', 'error')
        return redirect(url_for('admin.singers'))

    fallback = Singer.query.filter_by(slug='other-artists').first()
    if fallback is None and singer.samples.count() > 0:
        flash('لا يمكن حذف فنان مرتبط بأعمال قبل إضافة فنان بديل', 'error')
        return redirect(url_for('admin.singers'))

    if singer.slug == 'other-artists':
        sole_samples = [sample for sample in singer.samples.all() if len(sample.singers) <= 1]
        if sole_samples:
            flash('لا يمكن حذف فنانين آخرين لأنه الفنان الوحيد لبعض الأعمال', 'error')
            return redirect(url_for('admin.singers'))

    for sample in singer.samples.all():
        if len(sample.singers) <= 1 and fallback is not None and fallback.id != singer.id:
            sample.singers.append(fallback)
        if singer in sample.singers:
            sample.singers.remove(singer)

    db.session.delete(singer)
    db.session.commit()
    flash('تم حذف الفنان بنجاح', 'success')
    return redirect(url_for('admin.singers'))


@admin_bp.route('/samples/add', methods=['GET', 'POST'])
@admin_required
def add_sample():
    categories = get_sample_categories()
    singers = get_singers()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category_id = request.form.get('category_id', type=int)
        media_type = request.form.get('media_type', 'youtube')
        is_featured = request.form.get('is_featured') == 'on'
        selected_category = db.session.get(Category, category_id) if category_id else None
        selected_singers, singer_errors = get_selected_singers()

        if not title or selected_category is None or singer_errors:
            flash('العنوان والقسم والفنان مطلوبة', 'error')
            for error in singer_errors:
                flash(error, 'error')
            return redirect(request.url)

        media_url = ''
        cover_image = None

        if media_type == 'youtube':
            media_url = request.form.get('youtube_url', '').strip()
        else:
            media_url = save_file(request.files.get('media_file'))
            cover_image = save_file(request.files.get('cover_image'))

        if not media_url:
            flash('العنوان والقسم والملف أو الرابط مطلوبة', 'error')
            return redirect(request.url)

        sample = Sample(
            title=title,
            category_id=selected_category.id,
            media_type=media_type,
            media_url=media_url,
            cover_image=cover_image,
            is_featured=is_featured,
        )
        sample.singers = selected_singers
        db.session.add(sample)
        db.session.commit()
        flash('تمت إضافة العمل بنجاح', 'success')
        return redirect(url_for('admin.samples'))

    return render_template('admin/sample_form.html', categories=categories, singers=singers, sample=None)


@admin_bp.route('/samples/<int:sample_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_sample(sample_id):
    sample = db.session.get(Sample, sample_id)
    if not sample:
        flash('العمل غير موجود', 'error')
        return redirect(url_for('admin.samples'))

    categories = get_sample_categories()
    singers = get_singers()

    if request.method == 'POST':
        category_id = request.form.get('category_id', type=int)
        selected_category = db.session.get(Category, category_id) if category_id else None
        if selected_category is None:
            flash('القسم غير موجود', 'error')
            return redirect(request.url)
        selected_singers, singer_errors = get_selected_singers()
        if singer_errors:
            for error in singer_errors:
                flash(error, 'error')
            return redirect(request.url)

        sample.title = request.form.get('title', '').strip()
        if not sample.title:
            flash('العنوان مطلوب', 'error')
            return redirect(request.url)

        sample.category_id = selected_category.id
        sample.singers = selected_singers
        sample.is_featured = request.form.get('is_featured') == 'on'
        media_type = request.form.get('media_type', 'youtube')

        if media_type == 'youtube':
            sample.media_type = 'youtube'
            sample.media_url = request.form.get('youtube_url', '').strip()
            if not sample.media_url:
                flash('رابط YouTube مطلوب', 'error')
                return redirect(request.url)
        else:
            new_media = save_file(request.files.get('media_file'))
            if new_media:
                sample.media_url = new_media
                sample.media_type = 'upload'

            new_cover = save_file(request.files.get('cover_image'))
            if new_cover:
                sample.cover_image = new_cover

        db.session.commit()
        flash('تم تحديث العمل بنجاح', 'success')
        return redirect(url_for('admin.samples'))

    return render_template('admin/sample_form.html', categories=categories, singers=singers, sample=sample)


@admin_bp.route('/samples/<int:sample_id>/delete', methods=['POST'])
@admin_required
def delete_sample(sample_id):
    sample = db.session.get(Sample, sample_id)
    if not sample:
        flash('العمل غير موجود', 'error')
        return redirect(url_for('admin.samples'))

    for filename in [sample.media_url, sample.cover_image]:
        if filename and sample.media_type == 'upload' and not str(filename).startswith(('http://', 'https://')):
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)

    db.session.delete(sample)
    db.session.commit()
    flash('تم حذف العمل', 'success')
    return redirect(url_for('admin.samples'))


@admin_bp.route('/samples')
@admin_required
def samples():
    all_samples = (
        Sample.query.options(joinedload(Sample.category), selectinload(Sample.singers))
        .order_by(Sample.created_at.desc())
        .all()
    )
    return render_template('admin/samples.html', samples=all_samples)


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
                note=note or f'تم تحديث الحالة إلى: {order.status_label}',
            )
            db.session.add(tracking)
            db.session.commit()
            flash('تم تحديث حالة الطلب', 'success')

    tracking = order.tracking_updates.order_by(TrackingUpdate.created_at.asc()).all()
    return render_template('admin/order_detail.html', order=order, tracking=tracking)

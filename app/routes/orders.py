import urllib.parse
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Order, TrackingUpdate, Sample, Category

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/order/new', methods=['GET', 'POST'])
def new_order():
    categories = Category.query.order_by(Category.sort_order).all()
    samples = Sample.query.order_by(Sample.created_at.desc()).all()

    if request.method == 'POST':
        names_requested = request.form.get('names_requested', '').strip()
        occasion_type = request.form.get('occasion_type', '').strip()
        work_type = request.form.get('work_type', '').strip()
        details = request.form.get('details', '').strip()
        whatsapp_number = request.form.get('whatsapp_number', '').strip()
        reference_sample_id = request.form.get('reference_sample_id', None)
        order_method = request.form.get('order_method', 'whatsapp')

        if reference_sample_id:
            reference_sample_id = int(reference_sample_id)
        else:
            reference_sample_id = None

        # Validation
        errors = []
        if not names_requested:
            errors.append('الأسماء المطلوبة مطلوبة')
        if not occasion_type:
            errors.append('نوع المناسبة مطلوب')
        if not work_type:
            errors.append('نوع العمل مطلوب')
        if not whatsapp_number:
            errors.append('رقم الواتساب مطلوب')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('custom_order.html', categories=categories, samples=samples)

        # Guest flow: redirect to WhatsApp
        if order_method == 'whatsapp' or not current_user.is_authenticated:
            wa_number = current_app.config['WHATSAPP_NUMBER'].replace('+', '')
            ref_text = ''
            if reference_sample_id:
                ref_sample = db.session.get(Sample, reference_sample_id)
                if ref_sample:
                    ref_text = f'\nمرجع: {ref_sample.title}'

            message = (
                f'طلب جديد من سمو\n'
                f'━━━━━━━━━━\n'
                f'الأسماء: {names_requested}\n'
                f'المناسبة: {occasion_type}\n'
                f'نوع العمل: {work_type}\n'
                f'{ref_text}'
                f'\nالتفاصيل: {details}\n'
                f'رقم التواصل: {whatsapp_number}'
            )
            encoded = urllib.parse.quote(message)
            return redirect(f'https://wa.me/{wa_number}?text={encoded}')

        # Logged-in user flow: save to database
        order = Order(
            user_id=current_user.id,
            names_requested=names_requested,
            occasion_type=occasion_type,
            work_type=work_type,
            reference_sample_id=reference_sample_id,
            details=details,
            whatsapp_number=whatsapp_number,
            status='new'
        )
        db.session.add(order)
        db.session.commit()

        # Create initial tracking update
        tracking = TrackingUpdate(
            order_id=order.id,
            status='new',
            note='تم استلام الطلب بنجاح'
        )
        db.session.add(tracking)
        db.session.commit()

        flash('تم إرسال طلبك بنجاح! يمكنك متابعة حالته من لوحة التحكم', 'success')
        return redirect(url_for('orders.order_detail', order_id=order.id))

    # Pre-fill from quick order link
    ref_id = request.args.get('sample_id', None)
    return render_template('custom_order.html', categories=categories, samples=samples, ref_sample_id=ref_id)


@orders_bp.route('/dashboard')
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('dashboard/my_orders.html', orders=orders)


@orders_bp.route('/dashboard/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    tracking = order.tracking_updates.order_by(TrackingUpdate.created_at.asc()).all()
    return render_template('dashboard/order_detail.html', order=order, tracking=tracking)

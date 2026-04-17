from flask import Blueprint, render_template
from app.models import Sample, Category

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    featured_samples = Sample.query.filter_by(is_featured=True).order_by(Sample.created_at.desc()).limit(8).all()
    # If not enough featured, fill with recent samples
    if len(featured_samples) < 4:
        featured_samples = Sample.query.order_by(Sample.created_at.desc()).limit(8).all()
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('index.html', featured_samples=featured_samples, categories=categories)


@main_bp.route('/category/<slug>')
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()
    samples = Sample.query.filter_by(category_id=cat.id).order_by(Sample.created_at.desc()).all()
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('category.html', category=cat, samples=samples, categories=categories)


@main_bp.route('/about')
def about():
    return render_template('about.html')

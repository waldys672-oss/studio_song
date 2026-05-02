from flask import Blueprint, render_template
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models import Sample, Category

main_bp = Blueprint('main', __name__)


# @main_bp.route('/')
# def index():
#     featured_samples = Sample.query.filter_by(is_featured=True).order_by(Sample.created_at.desc()).limit(8).all()
#     categories = Category.query.order_by(Category.sort_order).all()
    
#     return render_template('index.html', featured_samples=featured_samples, categories=categories)
@main_bp.route('/')
def index():
    featured_samples = Sample.query.filter_by(is_featured=True).order_by(Sample.created_at.desc()).limit(8).all()
    # جلب الأقسام الرئيسية فقط (التي ليس لها parent_id)
    main_categories = Category.query.filter_by(parent_id=None).order_by(Category.sort_order).all()
    
    return render_template('index.html', featured_samples=featured_samples, categories=main_categories)

@main_bp.route('/category/<slug>')
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()

    # Only fetch samples that belong to this category.
    # If this is a main category, also include samples from its subcategories.
    sample_query = (
        Sample.query.join(Category, Sample.category_id == Category.id)
        .options(joinedload(Sample.category).joinedload(Category.parent))
        .order_by(Sample.created_at.desc())
    )
    if cat.parent_id is None:
        sample_query = sample_query.filter(or_(Category.id == cat.id, Category.parent_id == cat.id))
    else:
        sample_query = sample_query.filter(Category.id == cat.id)

    samples = sample_query.all()
    categories = Category.query.order_by(Category.sort_order).all()
    
    return render_template('category.html', category=cat, samples=samples, categories=categories)
@main_bp.route('/about')
def about():
    return render_template('about.html')

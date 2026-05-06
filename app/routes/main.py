from flask import Blueprint, abort, render_template, request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models import Category, Sample

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    main_categories = Category.query.filter_by(parent_id=None).order_by(Category.sort_order).all()

    sample_query = Sample.query.options(joinedload(Sample.category).joinedload(Category.parent))
    if search_query:
        sample_query = sample_query.filter(Sample.title.ilike(f'%{search_query}%')).order_by(
            Sample.is_featured.desc(),
            Sample.created_at.desc(),
        )
    else:
        sample_query = sample_query.filter_by(is_featured=True).order_by(Sample.created_at.desc()).limit(8)

    samples = sample_query.all()

    return render_template(
        'index.html',
        samples=samples,
        categories=main_categories,
        search_query=search_query,
    )

@main_bp.route('/sample/<int:sample_id>')
def sample_detail(sample_id):
    sample = (
        Sample.query.options(joinedload(Sample.category).joinedload(Category.parent))
        .filter_by(id=sample_id)
        .first()
    )
    if sample is None:
        abort(404)

    # For the back-to-category link and nav widgets.
    categories = Category.query.order_by(Category.sort_order).all()

    return render_template('sample.html', sample=sample, categories=categories)


@main_bp.route('/category/<slug>')
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()

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

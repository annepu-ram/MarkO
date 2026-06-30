from datetime import datetime
from decimal import Decimal, InvalidOperation
import re

from flask import Blueprint, abort, g, jsonify, request

from extensions import db
from guards import require_role
from models import Brand, Organization, Product, ProductBrand

product_bp = Blueprint('product', __name__)


@product_bp.before_request
def set_default_org():
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


def _slugify(value):
    slug = re.sub(r'[^a-z0-9]+', '-', (value or '').lower()).strip('-')
    return slug or 'product'


def _unique_product_slug(org_id, name, existing_id=None):
    base = _slugify(name)
    slug = base
    counter = 2
    while True:
        query = Product.query.filter_by(org_id=org_id, slug=slug)
        if existing_id:
            query = query.filter(Product.id != existing_id)
        if not query.first():
            return slug
        slug = f'{base}-{counter}'
        counter += 1


def _decimal_or_none(value, field_name):
    if value in (None, ''):
        return None, None
    try:
        return Decimal(str(value)), None
    except (InvalidOperation, ValueError):
        return None, f'{field_name} must be a number.'


def _brand_ids_for_org(brand_ids):
    if not brand_ids:
        return []
    if not isinstance(brand_ids, list):
        return None
    ids = [str(item) for item in brand_ids if item]
    if not ids:
        return []
    count = Brand.query.filter(
        Brand.org_id == g.current_org_id,
        Brand.id.in_(ids),
    ).count()
    if count != len(set(ids)):
        return None
    return list(dict.fromkeys(ids))


def _sync_product_brands(product, brand_ids):
    brand_ids = brand_ids or []
    existing = {pb.brand_id: pb for pb in product.brands}
    desired = set(brand_ids)

    for brand_id, link in list(existing.items()):
        if brand_id not in desired:
            db.session.delete(link)

    for index, brand_id in enumerate(brand_ids):
        if brand_id not in existing:
            db.session.add(ProductBrand(
                product_id=product.id,
                brand_id=brand_id,
                role='primary' if index == 0 else 'associated',
                sort_order=index,
            ))
        else:
            existing[brand_id].role = 'primary' if index == 0 else 'associated'
            existing[brand_id].sort_order = index


def _apply_product_fields(product, data):
    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return 'Product name is required.'
        product.name = name[:255]
        product.slug = _unique_product_slug(g.current_org_id, name, existing_id=product.id)

    for field in ['short_description', 'description', 'sku', 'default_image_url']:
        if field in data:
            value = data.get(field)
            setattr(product, field, (value or '').strip() or None)

    if 'status' in data:
        status = (data.get('status') or 'draft').strip()
        if status not in Product.VALID_STATUSES:
            return f'Invalid status. Must be one of: {", ".join(sorted(Product.VALID_STATUSES))}'
        product.status = status

    if 'product_type' in data:
        product_type = (data.get('product_type') or 'service').strip()
        if product_type not in Product.VALID_TYPES:
            return f'Invalid product_type. Must be one of: {", ".join(sorted(Product.VALID_TYPES))}'
        product.product_type = product_type

    if 'availability' in data:
        availability = (data.get('availability') or 'service_only').strip()
        if availability not in Product.VALID_AVAILABILITY:
            return f'Invalid availability. Must be one of: {", ".join(sorted(Product.VALID_AVAILABILITY))}'
        product.availability = availability

    if 'price' in data:
        price, error = _decimal_or_none(data.get('price'), 'price')
        if error:
            return error
        product.price = price

    if 'compare_at_price' in data:
        price, error = _decimal_or_none(data.get('compare_at_price'), 'compare_at_price')
        if error:
            return error
        product.compare_at_price = price

    if 'currency' in data:
        product.currency = (data.get('currency') or 'USD').strip().upper()[:10]

    if 'tags' in data:
        if not isinstance(data.get('tags'), list):
            return 'tags must be an array.'
        product.set_tags([str(item).strip() for item in data.get('tags') if str(item).strip()])

    if 'attributes' in data:
        if not isinstance(data.get('attributes'), dict):
            return 'attributes must be an object.'
        product.set_attributes(data.get('attributes'))

    product.updated_at = datetime.utcnow()
    return None


@product_bp.route('/api/products', methods=['GET'])
def list_products():
    query = Product.query.filter_by(org_id=g.current_org_id)

    status = request.args.get('status')
    if status and status in Product.VALID_STATUSES:
        query = query.filter_by(status=status)

    product_type = request.args.get('product_type')
    if product_type and product_type in Product.VALID_TYPES:
        query = query.filter_by(product_type=product_type)

    search = (request.args.get('q') or '').strip()
    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(
            Product.name.ilike(like),
            Product.short_description.ilike(like),
            Product.description.ilike(like),
            Product.sku.ilike(like),
        ))

    brand_id = request.args.get('brand_id')
    if brand_id:
        query = query.join(ProductBrand).filter(ProductBrand.brand_id == brand_id)

    products = query.order_by(Product.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in products])


@product_bp.route('/api/products', methods=['POST'])
@require_role('editor')
def create_product():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Product name is required.'}), 400

    product = Product(
        org_id=g.current_org_id,
        name=name[:255],
        slug=_unique_product_slug(g.current_org_id, name),
    )
    db.session.add(product)
    db.session.flush()

    error = _apply_product_fields(product, data)
    if error:
        db.session.rollback()
        return jsonify({'error': error}), 400

    if 'brand_ids' in data:
        brand_ids = _brand_ids_for_org(data.get('brand_ids'))
        if brand_ids is None:
            db.session.rollback()
            return jsonify({'error': 'One or more selected brands were not found.'}), 400
        _sync_product_brands(product, brand_ids)

    db.session.commit()
    return jsonify(product.to_dict()), 201


@product_bp.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.filter_by(id=product_id, org_id=g.current_org_id).first()
    if not product:
        abort(404)
    return jsonify(product.to_dict())


@product_bp.route('/api/products/<product_id>', methods=['PATCH'])
@require_role('editor')
def update_product(product_id):
    product = Product.query.filter_by(id=product_id, org_id=g.current_org_id).first()
    if not product:
        abort(404)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    error = _apply_product_fields(product, data)
    if error:
        return jsonify({'error': error}), 400

    if 'brand_ids' in data:
        brand_ids = _brand_ids_for_org(data.get('brand_ids'))
        if brand_ids is None:
            return jsonify({'error': 'One or more selected brands were not found.'}), 400
        _sync_product_brands(product, brand_ids)

    db.session.commit()
    return jsonify(product.to_dict())


@product_bp.route('/api/products/<product_id>', methods=['DELETE'])
@require_role('editor')
def archive_product(product_id):
    product = Product.query.filter_by(id=product_id, org_id=g.current_org_id).first()
    if not product:
        abort(404)
    product.status = 'archived'
    product.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


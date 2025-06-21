from flask import jsonify
from app.api import bp
from app.models import MenuItem, Category
from app.extensions import db

@bp.route('/health')
def health():
    """API health check"""
    return jsonify({'status': 'healthy', 'message': 'Restaurant API is running'})

@bp.route('/menu-items')
def get_menu_items():
    """Get all available menu items"""
    try:
        items = MenuItem.query.filter_by(status='available').all()
        menu_items = []

        for item in items:
            # Get default image URL based on category
            default_images = {
                'Hookah': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop',
                'Drinks': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=300&h=200&fit=crop',
                'Brunch': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=300&h=200&fit=crop',
                'Main Courses': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop',
                'Desserts': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=300&h=200&fit=crop'
            }

            category_name = item.category.name if item.category else 'Main Courses'
            image_url = item.image_url or default_images.get(category_name, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=300&h=200&fit=crop')

            menu_items.append({
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': category_name,
                'image': image_url,
                'stock': item.stock
            })

        return jsonify({
            'status': 'success',
            'data': menu_items
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@bp.route('/menu-items/suggested')
def get_suggested_items():
    """Get suggested menu items for cart"""
    try:
        # Get 3 random available items
        items = MenuItem.query.filter_by(status='available').limit(3).all()
        suggested_items = []

        for item in items:
            # Get default image URL based on category
            default_images = {
                'Hookah': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=80&h=80&fit=crop',
                'Drinks': 'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=80&h=80&fit=crop',
                'Brunch': 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=80&h=80&fit=crop',
                'Main Courses': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=80&h=80&fit=crop',
                'Desserts': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=80&h=80&fit=crop'
            }

            category_name = item.category.name if item.category else 'Main Courses'
            image_url = item.image_url or default_images.get(category_name, 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=80&h=80&fit=crop')

            suggested_items.append({
                'id': item.item_id,
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'category': category_name,
                'image': image_url
            })

        return jsonify({
            'status': 'success',
            'data': suggested_items
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

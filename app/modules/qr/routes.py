from flask import render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app.modules.qr import bp
from app.modules.qr.qr_service import QRCodeService
from app.models import Table, QRCode
from app.extensions import db
import os
import logging

logger = logging.getLogger(__name__)

@bp.route('/scan/<int:table_id>')
def scan_qr_code(table_id):
    """Handle QR code scan and redirect appropriately"""
    try:
        # Track the scan
        qr_service = QRCodeService()
        qr_type = request.args.get('type', 'menu')
        qr_service.track_qr_scan(table_id, qr_type)
        
        # Store table ID in session for later use
        session['table_id'] = table_id
        session['scanned_table'] = True
        
        # Redirect based on QR type and user status
        if qr_type == 'menu':
            return redirect(url_for('customer.menu', table_id=table_id))
        elif qr_type == 'login':
            if current_user.is_authenticated:
                return redirect(url_for('customer.menu', table_id=table_id))
            else:
                return redirect(url_for('auth.login', next=url_for('customer.menu', table_id=table_id)))
        elif qr_type == 'payment':
            if current_user.is_authenticated:
                # Get the latest order for this table/user
                from app.models import Order
                latest_order = Order.query.filter_by(
                    user_id=current_user.user_id,
                    table_number=str(table_id)
                ).order_by(Order.order_time.desc()).first()
                
                if latest_order and latest_order.status in ['new', 'confirmed']:
                    return redirect(url_for('payment.checkout', order_id=latest_order.id))
                else:
                    flash('No pending order found for payment.', 'info')
                    return redirect(url_for('customer.menu', table_id=table_id))
            else:
                return redirect(url_for('auth.login', next=url_for('customer.menu', table_id=table_id)))
        else:
            return redirect(url_for('main.index'))
    
    except Exception as e:
        logger.error(f"Error handling QR scan: {str(e)}")
        flash('Error processing QR code. Please try again.', 'error')
        return redirect(url_for('main.index'))

@bp.route('/generate/<int:table_id>')
@login_required
def generate_table_qr(table_id):
    """Generate QR code for a table (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_type = request.args.get('type', 'menu')
        qr_service = QRCodeService()
        result = qr_service.generate_table_qr_code(table_id, qr_type)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/generate-base64/<int:table_id>')
@login_required
def generate_qr_base64(table_id):
    """Generate QR code as base64 for inline display"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_type = request.args.get('type', 'menu')
        qr_service = QRCodeService()
        result = qr_service.generate_qr_as_base64(table_id, qr_type)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/bulk-generate', methods=['POST'])
@login_required
def bulk_generate_qr():
    """Generate QR codes for multiple tables"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        data = request.get_json()
        table_ids = data.get('table_ids', [])
        qr_type = data.get('type', 'menu')
        
        if not table_ids:
            return jsonify({'success': False, 'message': 'No table IDs provided'}), 400
        
        qr_service = QRCodeService()
        results = qr_service.generate_bulk_qr_codes(table_ids, qr_type)
        
        return jsonify({
            'success': True,
            'message': f'Generated QR codes for {len(table_ids)} tables',
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Error bulk generating QR codes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/table/<int:table_id>/codes')
@login_required
def get_table_qr_codes(table_id):
    """Get all QR codes for a specific table"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_service = QRCodeService()
        qr_codes = qr_service.get_table_qr_codes(table_id)
        
        return jsonify({
            'success': True,
            'table_id': table_id,
            'qr_codes': qr_codes
        })
    
    except Exception as e:
        logger.error(f"Error getting table QR codes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/analytics')
@login_required
def qr_analytics():
    """Get QR code usage analytics (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_service = QRCodeService()
        analytics = qr_service.get_qr_analytics()
        
        return jsonify(analytics)
    
    except Exception as e:
        logger.error(f"Error getting QR analytics: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/deactivate/<int:qr_id>', methods=['POST'])
@login_required
def deactivate_qr_code(qr_id):
    """Deactivate a QR code (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_service = QRCodeService()
        result = qr_service.deactivate_qr_code(qr_id)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error deactivating QR code: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/regenerate-all', methods=['POST'])
@login_required
def regenerate_all_qr_codes():
    """Regenerate all QR codes (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        qr_service = QRCodeService()
        result = qr_service.regenerate_all_qr_codes()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error regenerating QR codes: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/download/<int:table_id>')
@login_required
def download_qr_code(table_id):
    """Download QR code image file"""
    if not (current_user.is_admin() or current_user.is_waiter()):
        flash('Permission denied', 'error')
        return redirect(url_for('main.index'))
    
    try:
        qr_type = request.args.get('type', 'menu')
        filename = f"table_{table_id}_{qr_type}.png"
        filepath = os.path.join(current_app.static_folder, 'qr_codes', filename)
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            # Generate QR code if it doesn't exist
            qr_service = QRCodeService()
            result = qr_service.generate_table_qr_code(table_id, qr_type)
            
            if result['success']:
                return send_file(filepath, as_attachment=True, download_name=filename)
            else:
                flash('Error generating QR code', 'error')
                return redirect(url_for('main.index'))
    
    except Exception as e:
        logger.error(f"Error downloading QR code: {str(e)}")
        flash('Error downloading QR code', 'error')
        return redirect(url_for('main.index'))

@bp.route('/custom', methods=['POST'])
@login_required
def create_custom_qr():
    """Create a custom QR code with arbitrary data (admin only)"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        data = request.get_json()
        qr_data = data.get('data')
        filename = data.get('filename')
        
        if not qr_data:
            return jsonify({'success': False, 'message': 'QR data is required'}), 400
        
        qr_service = QRCodeService()
        result = qr_service.create_custom_qr_code(qr_data, filename)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error creating custom QR code: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/scanner')
def qr_scanner():
    """QR code scanner page for mobile devices"""
    return render_template('qr/scanner.html')

@bp.route('/management')
@login_required
def qr_management():
    """QR code management dashboard (admin only)"""
    if not current_user.is_admin():
        flash('Permission denied', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Get all tables
        tables = Table.query.all()
        
        # Get QR analytics
        qr_service = QRCodeService()
        analytics = qr_service.get_qr_analytics()
        
        return render_template('qr/management.html', 
                             tables=tables, 
                             analytics=analytics)
    
    except Exception as e:
        logger.error(f"Error loading QR management: {str(e)}")
        flash('Error loading QR management page', 'error')
        return redirect(url_for('admin.dashboard'))

from flask import current_app

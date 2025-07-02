from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
from app.modules.payment import bp
from app.modules.payment.payment_service import PaymentService
from app.models import Order, Payment
from app.extensions import db
from sqlalchemy.orm import joinedload
import logging

logger = logging.getLogger(__name__)

@bp.route('/checkout/<int:order_id>')
@login_required
def checkout(order_id):
    """Display the payment checkout page for an order."""
    try:
        order = Order.query.options(joinedload(Order.table)).get_or_404(order_id)
        
        # Check if user has permission to pay for this order
        if order.user_id != current_user.user_id and not current_user.is_admin():
            flash('You do not have permission to pay for this order.', 'error')
            return redirect(url_for('customer.my_orders'))
        
        # Check if order is already paid
        if order.status == 'paid':
            flash('This order has already been paid for.', 'info')
            return redirect(url_for('customer.my_orders'))
        
        # Get available payment methods
        payment_service = PaymentService()
        payment_methods = payment_service.get_payment_methods()
        
        return render_template('payment/checkout.html', 
                             order=order, 
                             payment_methods=payment_methods)
    
    except Exception as e:
        logger.error(f"Error displaying checkout page: {str(e)}")
        flash('An error occurred while loading the checkout page.', 'error')
        return redirect(url_for('customer.my_orders'))

@bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process a payment for an order."""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        payment_method = data.get('payment_method')
        amount = data.get('amount')
        
        if not all([order_id, payment_method, amount]):
            return jsonify({
                'success': False,
                'message': 'Missing required payment information'
            }), 400
        
        # Get the order
        order = Order.query.get_or_404(order_id)
        
        # Check permissions
        if order.user_id != current_user.user_id and not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'You do not have permission to pay for this order'
            }), 403
        
        # Check if already paid
        if order.status == 'paid':
            return jsonify({
                'success': False,
                'message': 'This order has already been paid for'
            }), 400
        
        # Process payment
        payment_service = PaymentService()
        payment_data = {
            'amount': float(amount),
            'method': payment_method,
            'customer_id': current_user.user_id
        }
        result = payment_service.process_payment(order_id, payment_data)
        
        if result['success']:
            # Update order status
            order.status = 'paid'
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Payment processed successfully',
                'payment_id': result['payment_id'],
                'receipt_url': url_for('payment.receipt', payment_id=result['payment_id'])
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
    
    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing the payment'
        }), 500

@bp.route('/receipt/<int:payment_id>')
@login_required
def receipt(payment_id):
    """Display the payment receipt."""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Check permissions - payment belongs to user through order
        if payment.order.user_id != current_user.user_id and not current_user.is_admin():
            flash('You do not have permission to view this receipt.', 'error')
            return redirect(url_for('customer.my_orders'))
        
        # Generate receipt data
        payment_service = PaymentService()
        receipt_data = payment_service.generate_receipt(payment_id)
        
        return render_template('payment/receipt.html', 
                             payment=payment, 
                             receipt_data=receipt_data)
    
    except Exception as e:
        logger.error(f"Error displaying receipt: {str(e)}")
        flash('An error occurred while loading the receipt.', 'error')
        return redirect(url_for('customer.my_orders'))

@bp.route('/history')
@login_required
def payment_history():
    """Display payment history for the current user."""
    try:
        if current_user.is_admin():
            # Admin can see all payments
            payments = Payment.query.order_by(Payment.timestamp.desc()).all()
        else:
            # Regular users see only their payments through orders
            payments = Payment.query.join(Order).filter(
                Order.user_id == current_user.user_id
            ).order_by(Payment.timestamp.desc()).all()
        
        return render_template('payment/history.html', payments=payments)
    
    except Exception as e:
        logger.error(f"Error displaying payment history: {str(e)}")
        flash('An error occurred while loading payment history.', 'error')
        return redirect(url_for('main.index'))

@bp.route('/refund/<int:payment_id>', methods=['POST'])
@login_required
def refund_payment(payment_id):
    """Process a refund for a payment (admin only)."""
    try:
        if not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'Only administrators can process refunds'
            }), 403
        
        data = request.get_json()
        refund_amount = data.get('refund_amount')
        reason = data.get('reason', 'Admin refund')
        
        payment_service = PaymentService()
        result = payment_service.process_refund(
            payment_id=payment_id,
            refund_amount=float(refund_amount) if refund_amount else None,
            reason=reason
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Refund processed successfully',
                'refund_id': result.get('refund_id')
            })
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
    
    except Exception as e:
        logger.error(f"Error processing refund: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing the refund'
        }), 500

@bp.route('/status/<int:payment_id>')
@login_required
def payment_status(payment_id):
    """Get the status of a payment."""
    try:
        payment = Payment.query.get_or_404(payment_id)
        
        # Check permissions - payment belongs to user through order
        if payment.order.user_id != current_user.user_id and not current_user.is_admin():
            return jsonify({
                'success': False,
                'message': 'You do not have permission to view this payment'
            }), 403
        
        return jsonify({
            'success': True,
            'payment_id': payment.payment_id,
            'status': payment.status,
            'amount': str(payment.amount),
            'payment_type': payment.payment_type,
            'timestamp': payment.timestamp.isoformat(),
            'transaction_id': payment.transaction_id
        })
    
    except Exception as e:
        logger.error(f"Error getting payment status: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while checking payment status'
        }), 500

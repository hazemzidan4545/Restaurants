"""
Payment API Endpoints
RESTful API for payment processing and management
"""
from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.modules.payment.api import bp
from app.modules.payment.payment_service import PaymentService
from app.models import Payment, Order, db
from datetime import datetime

@bp.route('/methods', methods=['GET'])
def get_payment_methods():
    """Get available payment methods"""
    try:
        methods = PaymentService.get_payment_methods()
        return jsonify({
            'success': True,
            'data': methods
        })
    except Exception as e:
        current_app.logger.error(f"Error getting payment methods: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get payment methods'
        }), 500

@bp.route('/process', methods=['POST'])
@login_required
def process_payment():
    """Process a payment for an order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('order_id'):
            return jsonify({
                'success': False,
                'error': 'Order ID is required'
            }), 400
        
        if not data.get('method'):
            return jsonify({
                'success': False,
                'error': 'Payment method is required'
            }), 400
        
        if not data.get('amount'):
            return jsonify({
                'success': False,
                'error': 'Payment amount is required'
            }), 400
        
        # Verify order belongs to current user (for customers)
        order = Order.query.get(data['order_id'])
        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404
        
        # For customers, verify they own the order
        if current_user.role == 'customer' and order.user_id != current_user.user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized to pay for this order'
            }), 403
        
        # Process the payment
        payment_data = {
            'method': data['method'],
            'amount': data['amount'],
            'card_details': data.get('card_details', {}),
            'billing_address': data.get('billing_address', {}),
            'customer_id': current_user.user_id
        }
        
        result = PaymentService.process_payment(data['order_id'], payment_data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"Payment processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Payment processing failed'
        }), 500

@bp.route('/status/<int:payment_id>', methods=['GET'])
@login_required
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({
                'success': False,
                'error': 'Payment not found'
            }), 404
        
        # Verify access permissions
        order = Order.query.get(payment.order_id)
        if current_user.role == 'customer' and order.user_id != current_user.user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        return jsonify({
            'success': True,
            'data': {
                'payment_id': payment.payment_id,
                'order_id': payment.order_id,
                'amount': float(payment.amount),
                'payment_type': payment.payment_type,
                'status': payment.status,
                'transaction_id': payment.transaction_id,
                'timestamp': payment.timestamp.isoformat()
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting payment status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get payment status'
        }), 500

@bp.route('/receipt/<int:payment_id>', methods=['GET'])
@login_required
def get_receipt(payment_id):
    """Generate and get receipt for a payment"""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({
                'success': False,
                'error': 'Payment not found'
            }), 404
        
        # Verify access permissions
        order = Order.query.get(payment.order_id)
        if current_user.role == 'customer' and order.user_id != current_user.user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        receipt_data = PaymentService.generate_receipt(payment_id)
        if not receipt_data:
            return jsonify({
                'success': False,
                'error': 'Failed to generate receipt'
            }), 500
        
        return jsonify({
            'success': True,
            'data': receipt_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating receipt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate receipt'
        }), 500

@bp.route('/refund', methods=['POST'])
@login_required
def process_refund():
    """Process a payment refund (admin/waiter only)"""
    try:
        # Check permissions
        if current_user.role not in ['admin', 'waiter']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        data = request.get_json()
        
        if not data.get('payment_id'):
            return jsonify({
                'success': False,
                'error': 'Payment ID is required'
            }), 400
        
        refund_amount = data.get('refund_amount')
        
        result = PaymentService.refund_payment(data['payment_id'], refund_amount)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"Refund processing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Refund processing failed'
        }), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_payment_history():
    """Get payment history for current user"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if current_user.role == 'customer':
            # Get payments for user's orders
            payments_query = Payment.query.join(Order).filter(
                Order.user_id == current_user.user_id
            )
        else:
            # Admin/waiter can see all payments
            payments_query = Payment.query
        
        payments = payments_query.order_by(
            Payment.timestamp.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        payment_data = []
        for payment in payments.items:
            order = Order.query.get(payment.order_id)
            payment_data.append({
                'payment_id': payment.payment_id,
                'order_id': payment.order_id,
                'amount': float(payment.amount),
                'payment_type': payment.payment_type,
                'status': payment.status,
                'transaction_id': payment.transaction_id,
                'timestamp': payment.timestamp.isoformat(),
                'customer_name': order.customer.name if order.customer else 'Walk-in',
                'table_id': order.table_id
            })
        
        return jsonify({
            'success': True,
            'data': {
                'payments': payment_data,
                'pagination': {
                    'page': payments.page,
                    'pages': payments.pages,
                    'per_page': payments.per_page,
                    'total': payments.total,
                    'has_next': payments.has_next,
                    'has_prev': payments.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting payment history: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get payment history'
        }), 500

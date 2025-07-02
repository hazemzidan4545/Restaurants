"""
Payment Service
Handles payment processing, gateway integration, and transaction management
"""
from app.models import Payment, Order, db
from datetime import datetime
from flask import current_app
import uuid
import json

class PaymentService:
    """Main payment processing service"""
    
    @staticmethod
    def process_payment(order_id, payment_data):
        """
        Process payment for an order
        
        Args:
            order_id (int): Order ID
            payment_data (dict): Payment information including method, amount, etc.
            
        Returns:
            dict: Payment result with success status and details
        """
        try:
            # Get the order
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found',
                    'code': 'ORDER_NOT_FOUND'
                }
            
            # Validate payment amount
            if float(payment_data.get('amount', 0)) != float(order.total_amount):
                return {
                    'success': False,
                    'error': 'Payment amount does not match order total',
                    'code': 'AMOUNT_MISMATCH'
                }
            
            # Create payment record
            payment = Payment(
                order_id=order_id,
                amount=payment_data['amount'],
                payment_type=payment_data['method'],
                status='pending',
                transaction_id=str(uuid.uuid4())
            )
            db.session.add(payment)
            
            # Process based on payment method
            payment_method = payment_data['method']
            
            if payment_method == 'cash':
                result = PaymentService._process_cash_payment(payment, payment_data)
            elif payment_method in ['card', 'credit']:
                result = PaymentService._process_card_payment(payment, payment_data)
            elif payment_method == 'pos':
                result = PaymentService._process_pos_payment(payment, payment_data)
            elif payment_method in ['instapay', 'apple', 'wallet']:
                result = PaymentService._process_digital_wallet_payment(payment, payment_data)
            else:
                result = {
                    'success': False,
                    'error': 'Unsupported payment method',
                    'code': 'UNSUPPORTED_METHOD'
                }
            
            if result['success']:
                # Update order status if payment successful
                order.status = 'confirmed'
                order.payment_status = 'paid'
                
                # Award loyalty points if customer has loyalty account
                from app.modules.loyalty.loyalty_service import award_points_for_order
                if order.user_id:
                    award_points_for_order(order_id, order.user_id)
                
                db.session.commit()
                
                current_app.logger.info(f"Payment processed successfully for order {order_id}")
                
                return {
                    'success': True,
                    'payment_id': payment.payment_id,
                    'transaction_id': payment.transaction_id,
                    'order_status': order.status,
                    'message': 'Payment processed successfully'
                }
            else:
                payment.status = 'failed'
                db.session.commit()
                return result
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Payment processing error: {str(e)}")
            return {
                'success': False,
                'error': 'Payment processing failed',
                'code': 'PROCESSING_ERROR'
            }
    
    @staticmethod
    def _process_cash_payment(payment, payment_data):
        """Process cash payment (always successful for restaurant)"""
        payment.status = 'completed'
        return {
            'success': True,
            'method': 'cash',
            'message': 'Cash payment accepted'
        }
    
    @staticmethod
    def _process_card_payment(payment, payment_data):
        """Process credit/debit card payment"""
        # In a real implementation, this would integrate with payment gateways
        # For now, simulate processing
        
        card_data = payment_data.get('card_details', {})
        
        # Basic validation
        if not card_data.get('number') or not card_data.get('cvv'):
            payment.status = 'failed'
            return {
                'success': False,
                'error': 'Invalid card details',
                'code': 'INVALID_CARD'
            }
        
        # Simulate gateway processing (90% success rate)
        import random
        if random.random() < 0.9:
            payment.status = 'completed'
            payment.transaction_id = f"card_{uuid.uuid4().hex[:12]}"
            return {
                'success': True,
                'method': 'card',
                'transaction_id': payment.transaction_id,
                'message': 'Card payment processed successfully'
            }
        else:
            payment.status = 'failed'
            return {
                'success': False,
                'error': 'Card payment declined',
                'code': 'CARD_DECLINED'
            }
    
    @staticmethod
    def _process_pos_payment(payment, payment_data):
        """Process POS terminal payment"""
        # Simulate POS processing
        payment.status = 'completed'
        payment.transaction_id = f"pos_{uuid.uuid4().hex[:12]}"
        return {
            'success': True,
            'method': 'pos',
            'transaction_id': payment.transaction_id,
            'message': 'POS payment processed successfully'
        }
    
    @staticmethod
    def _process_digital_wallet_payment(payment, payment_data):
        """Process digital wallet payments (Instapay, Apple Pay, etc.)"""
        wallet_type = payment.payment_type
        
        # Simulate wallet processing
        payment.status = 'completed'
        payment.transaction_id = f"{wallet_type}_{uuid.uuid4().hex[:12]}"
        return {
            'success': True,
            'method': wallet_type,
            'transaction_id': payment.transaction_id,
            'message': f'{wallet_type.title()} payment processed successfully'
        }
    
    @staticmethod
    def refund_payment(payment_id, refund_amount=None):
        """
        Process payment refund
        
        Args:
            payment_id (int): Payment ID to refund
            refund_amount (float): Amount to refund (None for full refund)
            
        Returns:
            dict: Refund result
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return {
                    'success': False,
                    'error': 'Payment not found',
                    'code': 'PAYMENT_NOT_FOUND'
                }
            
            if payment.status != 'completed':
                return {
                    'success': False,
                    'error': 'Can only refund completed payments',
                    'code': 'INVALID_STATUS'
                }
            
            refund_amount = refund_amount or payment.amount
            
            if refund_amount > payment.amount:
                return {
                    'success': False,
                    'error': 'Refund amount cannot exceed payment amount',
                    'code': 'INVALID_AMOUNT'
                }
            
            # Process refund based on original payment method
            if payment.payment_type == 'cash':
                # Cash refunds handled manually
                status = 'completed'
            else:
                # For card/digital payments, simulate gateway refund
                status = 'completed'  # In real implementation, this would be async
            
            # Create refund record (we could extend Payment model or create RefundTransaction)
            payment.status = 'refunded'
            
            # Update order status
            order = Order.query.get(payment.order_id)
            if order:
                order.status = 'refunded'
                order.payment_status = 'refunded'
            
            db.session.commit()
            
            return {
                'success': True,
                'refund_amount': float(refund_amount),
                'refund_id': f"rf_{uuid.uuid4().hex[:12]}",
                'message': 'Refund processed successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Refund processing error: {str(e)}")
            return {
                'success': False,
                'error': 'Refund processing failed',
                'code': 'REFUND_ERROR'
            }
    
    @staticmethod
    def get_payment_methods():
        """Get available payment methods"""
        return [
            {
                'id': 'cash',
                'name': 'Cash',
                'icon': 'fas fa-money-bill-wave',
                'description': 'Pay with cash at the table',
                'enabled': True
            },
            {
                'id': 'pos',
                'name': 'POS Terminal',
                'icon': 'fas fa-credit-card',
                'description': 'Pay with card via POS terminal',
                'enabled': True
            },
            {
                'id': 'credit',
                'name': 'Credit Card',
                'icon': 'fas fa-credit-card',
                'description': 'Pay with credit/debit card online',
                'enabled': True
            },
            {
                'id': 'instapay',
                'name': 'Instapay',
                'icon': 'fas fa-mobile-alt',
                'description': 'Pay with Instapay mobile wallet',
                'enabled': True
            },
            {
                'id': 'apple',
                'name': 'Apple Pay',
                'icon': 'fab fa-apple',
                'description': 'Pay with Apple Pay',
                'enabled': True
            }
        ]
    
    @staticmethod
    def generate_receipt(payment_id):
        """Generate receipt data for a payment"""
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return None
            
            order = Order.query.get(payment.order_id)
            if not order:
                return None
            
            # Get order items
            order_items = []
            for item in order.order_items:
                order_items.append({
                    'name': item.menu_item.name,
                    'quantity': item.quantity,
                    'price': float(item.menu_item.price),
                    'total': float(item.quantity * item.menu_item.price),
                    'note': item.note
                })
            
            receipt_data = {
                'receipt_id': f"RCP-{payment.payment_id}-{datetime.now().strftime('%Y%m%d')}",
                'order_id': order.order_id,
                'payment_id': payment.payment_id,
                'transaction_id': payment.transaction_id,
                'date': payment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'customer': {
                    'name': order.customer.name if order.customer else 'Walk-in Customer',
                    'email': order.customer.email if order.customer else None,
                    'phone': order.customer.phone if order.customer else None
                },
                'table_number': order.table_id,
                'items': order_items,
                'subtotal': float(order.total_amount),
                'tax': 0.0,  # Add tax calculation if needed
                'total': float(payment.amount),
                'payment_method': payment.payment_type.title(),
                'status': payment.status.title(),
                'restaurant': {
                    'name': 'Restaurant Name',  # Get from config
                    'address': 'Restaurant Address',
                    'phone': 'Restaurant Phone',
                    'email': 'restaurant@email.com'
                }
            }
            
            return receipt_data
            
        except Exception as e:
            current_app.logger.error(f"Receipt generation error: {str(e)}")
            return None

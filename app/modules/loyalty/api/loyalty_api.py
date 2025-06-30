from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.modules.loyalty.api import bp
from app.models import (
    CustomerLoyalty, PointTransaction, RewardItem, RewardRedemption,
    LoyaltyProgram, PromotionalCampaign, Order, db
)
from datetime import datetime, timedelta
import uuid


@bp.route('/points', methods=['GET'])
@login_required
def get_customer_points():
    """Get customer's current points balance and recent transactions"""
    try:
        # Get or create customer loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
        if not loyalty:
            loyalty = CustomerLoyalty(user_id=current_user.user_id)
            db.session.add(loyalty)
            db.session.commit()

        # Get recent transactions (last 3 months)
        three_months_ago = datetime.utcnow() - timedelta(days=90)
        transactions = PointTransaction.query.filter_by(
            user_id=current_user.user_id
        ).filter(
            PointTransaction.timestamp >= three_months_ago
        ).order_by(PointTransaction.timestamp.desc()).limit(20).all()

        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'transaction_id': transaction.transaction_id,
                'points_earned': transaction.points_earned,
                'points_redeemed': transaction.points_redeemed,
                'transaction_type': transaction.transaction_type,
                'description': transaction.description,
                'timestamp': transaction.timestamp.isoformat(),
                'expiry_date': transaction.expiry_date.isoformat() if transaction.expiry_date else None
            })

        return jsonify({
            'status': 'success',
            'data': {
                'total_points': loyalty.total_points,
                'lifetime_points': loyalty.lifetime_points,
                'tier_level': loyalty.tier_level,
                'join_date': loyalty.join_date.isoformat(),
                'transactions': transaction_data
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting customer points: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get points balance'
        }), 500


@bp.route('/rewards', methods=['GET'])
@login_required
def get_available_rewards():
    """Get available rewards for point redemption"""
    try:
        # Get customer's current points
        loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
        user_points = loyalty.total_points if loyalty else 0

        # Get active rewards
        rewards = RewardItem.query.filter_by(status='active').filter(
            db.or_(
                RewardItem.expiry_date.is_(None),
                RewardItem.expiry_date > datetime.utcnow()
            )
        ).order_by(RewardItem.points_required.asc()).all()

        reward_data = []
        for reward in rewards:
            reward_data.append({
                'reward_id': reward.reward_id,
                'name': reward.name,
                'description': reward.description,
                'points_required': reward.points_required,
                'category': reward.category,
                'can_redeem': user_points >= reward.points_required,
                'expiry_date': reward.expiry_date.isoformat() if reward.expiry_date else None
            })

        return jsonify({
            'status': 'success',
            'data': {
                'user_points': user_points,
                'rewards': reward_data
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting available rewards: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get available rewards'
        }), 500


@bp.route('/redeem', methods=['POST'])
@login_required
def redeem_reward():
    """Redeem a reward for points"""
    try:
        data = request.get_json()
        reward_id = data.get('reward_id')
        
        if not reward_id:
            return jsonify({
                'status': 'error',
                'message': 'Reward ID is required'
            }), 400

        # Get reward
        reward = RewardItem.query.get(reward_id)
        if not reward or reward.status != 'active':
            return jsonify({
                'status': 'error',
                'message': 'Reward not found or inactive'
            }), 404

        # Check if reward is expired
        if reward.expiry_date and reward.expiry_date < datetime.utcnow():
            return jsonify({
                'status': 'error',
                'message': 'Reward has expired'
            }), 400

        # Get customer loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
        if not loyalty:
            return jsonify({
                'status': 'error',
                'message': 'Customer loyalty account not found'
            }), 404

        # Check if customer has enough points
        if loyalty.total_points < reward.points_required:
            return jsonify({
                'status': 'error',
                'message': 'Insufficient points for redemption'
            }), 400

        # Create redemption record
        redemption_code = str(uuid.uuid4())[:8].upper()
        redemption = RewardRedemption(
            user_id=current_user.user_id,
            reward_id=reward_id,
            points_used=reward.points_required,
            redemption_code=redemption_code,
            status='completed'
        )
        db.session.add(redemption)

        # Deduct points from customer
        loyalty.total_points -= reward.points_required
        
        # Create point transaction record
        transaction = PointTransaction(
            user_id=current_user.user_id,
            points_redeemed=reward.points_required,
            transaction_type='redeemed',
            description=f'Redeemed: {reward.name}'
        )
        db.session.add(transaction)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'data': {
                'redemption_id': redemption.redemption_id,
                'redemption_code': redemption_code,
                'points_used': reward.points_required,
                'remaining_points': loyalty.total_points,
                'reward_name': reward.name
            }
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error redeeming reward: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to redeem reward'
        }), 500


@bp.route('/redemption-history', methods=['GET'])
@login_required
def get_redemption_history():
    """Get customer's redemption history"""
    try:
        redemptions = RewardRedemption.query.filter_by(
            user_id=current_user.user_id
        ).order_by(RewardRedemption.redemption_date.desc()).limit(50).all()

        history_data = []
        for redemption in redemptions:
            history_data.append({
                'redemption_id': redemption.redemption_id,
                'reward_name': redemption.reward.name,
                'points_used': redemption.points_used,
                'redemption_date': redemption.redemption_date.isoformat(),
                'redemption_code': redemption.redemption_code,
                'status': redemption.status
            })

        return jsonify({
            'status': 'success',
            'data': {'redemptions': history_data}
        })

    except Exception as e:
        current_app.logger.error(f"Error getting redemption history: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get redemption history'
        }), 500


@bp.route('/tier-progress', methods=['GET'])
@login_required
def get_tier_progress():
    """Get customer's tier progress and benefits"""
    try:
        loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
        if not loyalty:
            return jsonify({
                'status': 'error',
                'message': 'Customer loyalty account not found'
            }), 404

        # Define tier thresholds
        tier_thresholds = {
            'bronze': {'min': 0, 'max': 1999, 'benefits': ['Basic rewards', 'Birthday bonus']},
            'silver': {'min': 2000, 'max': 4999, 'benefits': ['10% bonus points', 'Priority support', 'Exclusive offers']},
            'gold': {'min': 5000, 'max': 9999, 'benefits': ['15% bonus points', 'Free delivery', 'VIP events']},
            'platinum': {'min': 10000, 'max': None, 'benefits': ['20% bonus points', 'Personal concierge', 'Elite rewards']}
        }

        current_tier = loyalty.tier_level
        current_points = loyalty.lifetime_points
        
        # Calculate next tier
        next_tier = None
        points_to_next = None
        
        if current_tier == 'bronze' and current_points < 2000:
            next_tier = 'silver'
            points_to_next = 2000 - current_points
        elif current_tier == 'silver' and current_points < 5000:
            next_tier = 'gold'
            points_to_next = 5000 - current_points
        elif current_tier == 'gold' and current_points < 10000:
            next_tier = 'platinum'
            points_to_next = 10000 - current_points

        return jsonify({
            'status': 'success',
            'data': {
                'current_tier': current_tier,
                'lifetime_points': current_points,
                'current_benefits': tier_thresholds[current_tier]['benefits'],
                'next_tier': next_tier,
                'points_to_next_tier': points_to_next,
                'tier_thresholds': tier_thresholds
            }
        })

    except Exception as e:
        current_app.logger.error(f"Error getting tier progress: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to get tier progress'
        }), 500

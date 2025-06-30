"""
Loyalty Program Service Functions
Handles point calculations, tier updates, and automated rewards
"""
from app.models import (
    CustomerLoyalty, PointTransaction, LoyaltyProgram, Order, db
)
from datetime import datetime, timedelta
from flask import current_app


def award_points_for_order(order_id, user_id):
    """
    Award points to customer when order is completed
    Standard rate: 100 points per 50 EGP spent
    """
    try:
        # Get the order
        order = Order.query.get(order_id)
        if not order or order.status != 'completed':
            return False

        # Check if points already awarded for this order
        existing_transaction = PointTransaction.query.filter_by(
            order_id=order_id,
            transaction_type='earned'
        ).first()
        
        if existing_transaction:
            current_app.logger.info(f"Points already awarded for order {order_id}")
            return True

        # Get or create customer loyalty account
        loyalty = CustomerLoyalty.query.filter_by(user_id=user_id).first()
        if not loyalty:
            loyalty = CustomerLoyalty(user_id=user_id)
            db.session.add(loyalty)

        # Get active loyalty program (or use default)
        program = LoyaltyProgram.query.filter_by(status='active').first()
        if not program:
            # Create default program if none exists
            program = LoyaltyProgram(
                name='Default Rewards Program',
                description='Earn points on every purchase',
                points_per_50EGP=100,
                status='active'
            )
            db.session.add(program)

        # Calculate points (100 points per 50 EGP)
        points_to_award = int((float(order.total_amount) / 50.0) * program.points_per_50EGP)
        
        # Check for promotional campaigns
        active_campaigns = get_active_campaigns()
        bonus_multiplier = 1.0
        campaign_description = ""
        
        for campaign in active_campaigns:
            if is_eligible_for_campaign(user_id, campaign):
                bonus_multiplier = max(bonus_multiplier, campaign.bonus_multiplier)
                campaign_description = f" (+ {campaign.name} bonus)"

        # Apply bonus multiplier
        final_points = int(points_to_award * bonus_multiplier)
        
        # Update customer loyalty
        loyalty.total_points += final_points
        loyalty.lifetime_points += final_points
        loyalty.last_activity = datetime.utcnow()
        
        # Update tier if necessary
        old_tier = loyalty.tier_level
        loyalty.update_tier()
        
        # Create point transaction record
        transaction = PointTransaction(
            user_id=user_id,
            order_id=order_id,
            points_earned=final_points,
            transaction_type='earned',
            description=f'Order #{order_id} - {order.total_amount} EGP{campaign_description}',
            expiry_date=datetime.utcnow() + timedelta(days=180)  # 6 months
        )
        db.session.add(transaction)

        # Award tier upgrade bonus if applicable
        if old_tier != loyalty.tier_level:
            tier_bonus_points = get_tier_upgrade_bonus(loyalty.tier_level)
            if tier_bonus_points > 0:
                loyalty.total_points += tier_bonus_points
                bonus_transaction = PointTransaction(
                    user_id=user_id,
                    points_earned=tier_bonus_points,
                    transaction_type='bonus',
                    description=f'Tier upgrade bonus - Welcome to {loyalty.tier_level.title()}!',
                    expiry_date=datetime.utcnow() + timedelta(days=180)
                )
                db.session.add(bonus_transaction)

        db.session.commit()
        
        current_app.logger.info(
            f"Awarded {final_points} points to user {user_id} for order {order_id}"
        )
        
        return True

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error awarding points for order {order_id}: {str(e)}")
        return False


def get_active_campaigns():
    """Get all active promotional campaigns"""
    from app.models import PromotionalCampaign
    
    now = datetime.utcnow()
    return PromotionalCampaign.query.filter(
        PromotionalCampaign.start_date <= now,
        PromotionalCampaign.end_date >= now
    ).all()


def is_eligible_for_campaign(user_id, campaign):
    """Check if user is eligible for a promotional campaign"""
    # Basic eligibility check - can be extended with more complex rules
    if not campaign.conditions:
        return True
    
    # Add custom campaign eligibility logic here
    # For now, all users are eligible for all campaigns
    return True


def get_tier_upgrade_bonus(tier_level):
    """Get bonus points for tier upgrades"""
    tier_bonuses = {
        'silver': 200,
        'gold': 500,
        'platinum': 1000
    }
    return tier_bonuses.get(tier_level, 0)


def expire_points():
    """
    Expire points that are older than 6 months
    This should be run as a scheduled task
    """
    try:
        six_months_ago = datetime.utcnow() - timedelta(days=180)
        
        # Find expired point transactions
        expired_transactions = PointTransaction.query.filter(
            PointTransaction.expiry_date <= datetime.utcnow(),
            PointTransaction.transaction_type == 'earned',
            PointTransaction.points_earned > 0
        ).all()

        total_expired_points = 0
        for transaction in expired_transactions:
            # Check if these points haven't been used yet
            user_loyalty = CustomerLoyalty.query.filter_by(
                user_id=transaction.user_id
            ).first()
            
            if user_loyalty and user_loyalty.total_points >= transaction.points_earned:
                # Deduct expired points
                user_loyalty.total_points -= transaction.points_earned
                
                # Create expiration transaction
                expiry_transaction = PointTransaction(
                    user_id=transaction.user_id,
                    points_redeemed=transaction.points_earned,
                    transaction_type='expired',
                    description=f'Points expired from {transaction.timestamp.strftime("%Y-%m-%d")}'
                )
                db.session.add(expiry_transaction)
                
                total_expired_points += transaction.points_earned

        db.session.commit()
        current_app.logger.info(f"Expired {total_expired_points} points")
        
        return total_expired_points

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error expiring points: {str(e)}")
        return 0


def calculate_points_for_amount(amount):
    """Calculate points for a given amount"""
    program = LoyaltyProgram.query.filter_by(status='active').first()
    if not program:
        return int((float(amount) / 50.0) * 100)  # Default: 100 points per 50 EGP
    
    return int((float(amount) / 50.0) * program.points_per_50EGP)


def get_customer_tier_benefits(tier_level):
    """Get benefits for a specific tier level"""
    benefits = {
        'bronze': {
            'point_bonus': 0,
            'benefits': ['Basic rewards', 'Birthday bonus points'],
            'description': 'Welcome tier for new members'
        },
        'silver': {
            'point_bonus': 10,
            'benefits': ['10% bonus points on all orders', 'Priority customer support', 'Exclusive monthly offers'],
            'description': 'Earned at 2,000 lifetime points'
        },
        'gold': {
            'point_bonus': 15,
            'benefits': ['15% bonus points on all orders', 'Free delivery on orders over 100 EGP', 'VIP event invitations'],
            'description': 'Earned at 5,000 lifetime points'
        },
        'platinum': {
            'point_bonus': 20,
            'benefits': ['20% bonus points on all orders', 'Personal concierge service', 'Elite exclusive rewards', 'Complimentary items'],
            'description': 'Earned at 10,000 lifetime points'
        }
    }
    
    return benefits.get(tier_level, benefits['bronze'])

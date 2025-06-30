from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.modules.loyalty import bp
from app.models import (
    CustomerLoyalty, PointTransaction, RewardItem, RewardRedemption,
    LoyaltyProgram, PromotionalCampaign, db
)
from app.modules.loyalty.loyalty_service import (
    get_customer_tier_benefits, calculate_points_for_amount
)
from datetime import datetime, timedelta


@bp.route('/')
@login_required
def index():
    """Customer loyalty dashboard"""
    # Get or create customer loyalty account
    loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
    if not loyalty:
        loyalty = CustomerLoyalty(user_id=current_user.user_id)
        db.session.add(loyalty)
        db.session.commit()

    # Get recent transactions
    transactions = PointTransaction.query.filter_by(
        user_id=current_user.user_id
    ).order_by(PointTransaction.timestamp.desc()).limit(10).all()

    # Get available rewards
    rewards = RewardItem.query.filter_by(status='active').filter(
        db.or_(
            RewardItem.expiry_date.is_(None),
            RewardItem.expiry_date > datetime.utcnow()
        )
    ).order_by(RewardItem.points_required.asc()).limit(6).all()

    # Get recent redemptions
    redemptions = RewardRedemption.query.filter_by(
        user_id=current_user.user_id
    ).order_by(RewardRedemption.redemption_date.desc()).limit(5).all()

    # Get tier benefits
    tier_benefits = get_customer_tier_benefits(loyalty.tier_level)

    # Calculate progress to next tier
    tier_thresholds = {
        'bronze': 2000,
        'silver': 5000,
        'gold': 10000,
        'platinum': float('inf')  # No tier above platinum
    }
    
    next_tier_info = None
    points_to_next = None
    progress_percentage = 0
    
    if loyalty.tier_level == 'bronze':
        next_tier_info = {
            'name': 'Silver',
            'threshold': tier_thresholds['silver']
        }
        points_to_next = tier_thresholds['silver'] - loyalty.lifetime_points
        progress_percentage = (loyalty.lifetime_points / tier_thresholds['silver']) * 100
    elif loyalty.tier_level == 'silver':
        next_tier_info = {
            'name': 'Gold',
            'threshold': tier_thresholds['gold']
        }
        points_to_next = tier_thresholds['gold'] - loyalty.lifetime_points
        progress_percentage = (loyalty.lifetime_points / tier_thresholds['gold']) * 100
    elif loyalty.tier_level == 'gold':
        next_tier_info = {
            'name': 'Platinum',
            'threshold': tier_thresholds['platinum']
        }
        points_to_next = tier_thresholds['platinum'] - loyalty.lifetime_points if tier_thresholds['platinum'] != float('inf') else 0
        progress_percentage = (loyalty.lifetime_points / tier_thresholds['platinum']) * 100 if tier_thresholds['platinum'] != float('inf') else 100
    else:  # platinum
        next_tier_info = None  # No next tier for platinum
        points_to_next = 0
        progress_percentage = 100

    # Get active campaigns
    now = datetime.utcnow()
    active_campaigns = PromotionalCampaign.query.filter(
        PromotionalCampaign.start_date <= now,
        PromotionalCampaign.end_date >= now
    ).all()

    return render_template('loyalty_dashboard.html',
                         loyalty=loyalty,
                         transactions=transactions,
                         rewards=rewards,
                         redemptions=redemptions,
                         tier_benefits=tier_benefits,
                         next_tier=next_tier_info,
                         points_to_next=max(0, points_to_next) if points_to_next else 0,
                         progress_percentage=min(100, progress_percentage),
                         active_campaigns=active_campaigns)


@bp.route('/rewards')
@login_required
def rewards_catalog():
    """Browse available rewards"""
    # Get customer's current points
    loyalty = CustomerLoyalty.query.filter_by(user_id=current_user.user_id).first()
    user_points = loyalty.total_points if loyalty else 0

    # Filter by category if specified
    category = request.args.get('category', '')
    
    query = RewardItem.query.filter_by(status='active').filter(
        db.or_(
            RewardItem.expiry_date.is_(None),
            RewardItem.expiry_date > datetime.utcnow()
        )
    )
    
    if category:
        query = query.filter_by(category=category)
    
    rewards = query.order_by(RewardItem.points_required.asc()).all()

    # Get available categories
    categories = db.session.query(RewardItem.category).filter_by(
        status='active'
    ).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]

    return render_template('loyalty_rewards.html',
                         rewards=rewards,
                         categories=categories,
                         selected_category=category,
                         user_points=user_points)


@bp.route('/history')
@login_required
def transaction_history():
    """View detailed transaction and redemption history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Get transactions
    transactions = PointTransaction.query.filter_by(
        user_id=current_user.user_id
    ).order_by(PointTransaction.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Get redemptions
    redemptions = RewardRedemption.query.filter_by(
        user_id=current_user.user_id
    ).order_by(RewardRedemption.redemption_date.desc()).all()

    return render_template('loyalty_history.html',
                         transactions=transactions,
                         redemptions=redemptions)

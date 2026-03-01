import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from datetime import datetime
from app.models.all_models import User, Subscription
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Stripe Client
stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscriptionService:
    """
    Handles all multi-tenant billing logic.
    Stripe Customers <-> Database Subscriptions <-> Role Limits.
    """

    @staticmethod
    async def create_checkout_session(db: AsyncSession, user: User, price_id: str, success_url: str, cancel_url: str) -> str:
        """
        Creates a Stripe Checkout Session for upgrading/subscribing.
        Returns the checkout URL.
        """
        try:
            # Check if user already has a Stripe customer ID
            stmt = select(Subscription).where(Subscription.user_id == user.id)
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()
            
            customer_id = subscription.stripe_customer_id if subscription else None
            
            # If no Stripe customer exists for this user, create one
            if not customer_id:
                customer = stripe.Customer.create(
                    email=user.email,
                    metadata={'user_id': user.id}
                )
                customer_id = customer.id
                
                # Update DB
                if subscription:
                    subscription.stripe_customer_id = customer_id
                else:
                    subscription = Subscription(user_id=user.id, stripe_customer_id=customer_id)
                    db.add(subscription)
                await db.commit()

            # Create the Checkout Session
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user.id # Important for webhook mapping
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Stripe Checkout Session Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize checkout.")

    @staticmethod
    async def process_webhook(db: AsyncSession, payload: bytes, sig_header: str) -> dict:
        """
        Validates and processes Stripe events (payments, cancellations, upgrades).
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        event_type = event['type']
        
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            await SubscriptionService._handle_checkout_completed(db, session)
            
        elif event_type == 'customer.subscription.updated':
            subscription_obj = event['data']['object']
            await SubscriptionService._handle_subscription_updated(db, subscription_obj)
            
        elif event_type == 'customer.subscription.deleted':
            subscription_obj = event['data']['object']
            await SubscriptionService._handle_subscription_deleted(db, subscription_obj)

        return {"status": "success", "event_type": event_type}


    @staticmethod
    async def _handle_checkout_completed(db: AsyncSession, session: dict):
        user_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        
        if not user_id:
            logger.warning("Checkout completed but no user_id found in client_reference_id.")
            return

        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User {user_id} not found during Stripe checkout completion.")
            return
            
        # Get or create subscription
        stmt = select(Subscription).where(Subscription.user_id == user_id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()
        
        if not sub:
             sub = Subscription(user_id=user_id, stripe_customer_id=customer_id)
             db.add(sub)
             
        # Because checkout completed, upgrade role!
        # Dynamically map the Stripe Price ID from session to our specific Plan ID & Role Type
        line_items = stripe.checkout.Session.list_line_items(session.get("id"))
        price_id = line_items.data[0].price.id if line_items.data else None
        
        # Mapping Logic
        role_type = "business_owner" # Default fallback
        plan_id = "free"
        
        if price_id == "price_solo_123":
            role_type = "business_owner"
            plan_id = "starter"
        elif price_id == "price_pro_123":
            role_type = "marketing_professional"
            plan_id = "growth"
        elif price_id == "price_agency_123":
            role_type = "agency_owner"
            plan_id = "agency"
            
        user.role_type = role_type
        sub.plan_id = plan_id
        sub.status = "active"
        sub.trial_active = False # Trial over since they paid
        
        await db.commit()
        logger.info(f"Successfully upgraded User {user_id} via Stripe Checkout. Role: {role_type}, Plan: {plan_id}")


    @staticmethod
    async def _handle_subscription_updated(db: AsyncSession, stripe_sub: dict):
        customer_id = stripe_sub.get('customer')
        status = stripe_sub.get('status') # active, past_due, canceled
        
        stmt = select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()
        
        if sub:
            sub.status = status
            period_end = stripe_sub.get('current_period_end')
            if period_end:
                 sub.current_period_end = datetime.fromtimestamp(period_end)
            await db.commit()
            logger.info(f"Subscription for Customer {customer_id} updated to {status}.")


    @staticmethod
    async def _handle_subscription_deleted(db: AsyncSession, stripe_sub: dict):
        customer_id = stripe_sub.get('customer')
        
        stmt = select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        result = await db.execute(stmt)
        sub = result.scalar_one_or_none()
        
        if sub:
            sub.status = "canceled"
            
            # Downgrade user back to free/business_owner
            stmt_user = select(User).where(User.id == sub.user_id)
            result_user = await db.execute(stmt_user)
            user = result_user.scalar_one_or_none()
            if user:
                 user.role_type = "business_owner" # Revoke premium limits
                 
            await db.commit()
            logger.info(f"Subscription canceled. User {sub.user_id} downgraded to base limits.")

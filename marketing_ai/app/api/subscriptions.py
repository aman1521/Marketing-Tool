from fastapi import APIRouter, Request, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.api.companies import get_current_user # Re-using dependency from companies api
from app.models.all_models import User

router = APIRouter()

@router.post("/checkout")
async def create_checkout(
    price_id: str, 
    success_url: str = "http://localhost:3000/success", 
    cancel_url: str = "http://localhost:3000/cancel",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Creates a Stripe Checkout session. Redirects the user to the Stripe portal to pay.
    """
    checkout_url = await SubscriptionService.create_checkout_session(
        db=db, user=user, price_id=price_id, success_url=success_url, cancel_url=cancel_url
    )
    return {"url": checkout_url}


@router.post("/webhook", include_in_schema=False) # Hide from Swagger as it's for Stripe
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)  
):
    """
    Stripe Webhook Listener. Updates the DB `role_type` dynamically based on payments/cancellations.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing signature header")
    
    # Must get the raw body bytes for Stripe signature validation!
    payload = await request.body()
    
    result = await SubscriptionService.process_webhook(
        db=db, payload=payload, sig_header=stripe_signature
    )
    
    return result

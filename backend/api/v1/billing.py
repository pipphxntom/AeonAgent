from fastapi import APIRouter

router = APIRouter()

# Placeholder for billing and subscription endpoints
@router.get("/subscription")
async def get_subscription():
    """Get current subscription."""
    return {"message": "Subscription endpoint - to be implemented"}

@router.post("/upgrade")
async def upgrade_subscription():
    """Upgrade subscription plan."""
    return {"message": "Upgrade endpoint - to be implemented"}

@router.post("/webhook/stripe")
async def stripe_webhook():
    """Handle Stripe webhooks."""
    return {"message": "Stripe webhook endpoint - to be implemented"}

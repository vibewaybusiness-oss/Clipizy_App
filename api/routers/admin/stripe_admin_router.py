from fastapi import APIRouter

# Create a placeholder router for Stripe admin functionality
router = APIRouter(prefix="/api/admin/stripe", tags=["Stripe Admin"])

@router.get("/health")
async def health_check():
    """Health check endpoint for Stripe admin router"""
    return {"status": "ok", "service": "stripe-admin"}

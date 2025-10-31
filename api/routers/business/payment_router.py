from fastapi import APIRouter

# Create a placeholder router for payment functionality
router = APIRouter(tags=["Payments"])

@router.get("/health")
async def health_check():
    """Health check endpoint for payment router"""
    return {"status": "ok", "service": "payments"}

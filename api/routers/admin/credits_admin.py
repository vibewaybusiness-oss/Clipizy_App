from fastapi import APIRouter

# Create a placeholder router for credits admin functionality
router = APIRouter(prefix="/api/admin/credits", tags=["Credits Admin"])

@router.get("/health")
async def health_check():
    """Health check endpoint for credits admin router"""
    return {"status": "ok", "service": "credits-admin"}

from fastapi import APIRouter

# Create a placeholder router for particle functionality
router = APIRouter(prefix="/api/particles", tags=["Particles"])

@router.get("/health")
async def health_check():
    """Health check endpoint for particle router"""
    return {"status": "ok", "service": "particles"}

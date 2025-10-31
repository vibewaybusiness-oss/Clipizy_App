from fastapi import APIRouter

# Create a placeholder router for automation functionality
router = APIRouter(prefix="/api/automation", tags=["Automation"])

@router.get("/health")
async def health_check():
    """Health check endpoint for automation router"""
    return {"status": "ok", "service": "automation"}

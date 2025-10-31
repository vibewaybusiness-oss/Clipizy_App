from fastapi import APIRouter

# Create a placeholder router for project functionality
router = APIRouter(tags=["Projects"])

@router.get("/health")
async def health_check():
    """Health check endpoint for project router"""
    return {"status": "ok", "service": "projects"}

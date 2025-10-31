from fastapi import APIRouter

# Create a placeholder router for export functionality
router = APIRouter(prefix="/api/export", tags=["Export"])

@router.get("/health")
async def health_check():
    """Health check endpoint for export router"""
    return {"status": "ok", "service": "export"}

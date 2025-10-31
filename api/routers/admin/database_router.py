from fastapi import APIRouter

# Create a placeholder router for database admin functionality
router = APIRouter(prefix="/api/admin/database", tags=["Database Admin"])

@router.get("/health")
async def health_check():
    """Health check endpoint for database admin router"""
    return {"status": "ok", "service": "database-admin"}

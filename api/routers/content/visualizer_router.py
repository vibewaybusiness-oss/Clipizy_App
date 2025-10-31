from fastapi import APIRouter

# Create a placeholder router for visualizer functionality
router = APIRouter(prefix="/api/visualizer", tags=["Visualizer"])

@router.get("/health")
async def health_check():
    """Health check endpoint for visualizer router"""
    return {"status": "ok", "service": "visualizer"}

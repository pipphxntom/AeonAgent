from fastapi import APIRouter

router = APIRouter()

# Placeholder for admin endpoints
@router.get("/stats")
async def get_platform_stats():
    """Get platform-wide statistics."""
    return {"message": "Admin stats endpoint - to be implemented"}

@router.get("/tenants")
async def list_all_tenants():
    """List all tenants (admin only)."""
    return {"message": "Admin tenants endpoint - to be implemented"}

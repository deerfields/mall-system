from fastapi import APIRouter

router = APIRouter(prefix="/api/tenants", tags=["tenants"])

@router.get("/")
def list_tenants():
    return [] 
from fastapi import APIRouter

router = APIRouter(prefix="/api/integration", tags=["integration"])

@router.get("/")
def list_integrations():
    return [] 
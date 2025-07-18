from fastapi import APIRouter

router = APIRouter(prefix="/api/finance", tags=["finance"])

@router.get("/")
def list_finance():
    return [] 
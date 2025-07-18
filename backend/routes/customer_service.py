from fastapi import APIRouter

router = APIRouter(prefix="/api/customer_service", tags=["customer_service"])

@router.get("/")
def list_customer_service():
    return [] 
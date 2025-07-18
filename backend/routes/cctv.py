from fastapi import APIRouter

router = APIRouter(prefix="/api/cctv", tags=["cctv"])

@router.get("/sample")
def sample_cctv():
    return {"message": "Sample CCTV endpoint"} 
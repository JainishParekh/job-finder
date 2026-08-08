from fastapi import APIRouter, Depends
from backend.service import verify_admin_access
from backend.database import get_db

router = APIRouter()


@router.get("/jobs")
def get_ready_jobs(token: str = Depends(verify_admin_access), db=Depends(get_db)):
    """
    Fetches all jobs from Supabase where the resume is ready.
    This route is fully protected by your API key.
    """
    # Query Supabase for your tailored jobs
    response = db.table("jobs").select("*").eq("status", "Ready").execute()

    return {"status": "success", "data": response.data}

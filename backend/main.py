from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.router import router

app = FastAPI(title="AI Agent Backend")

# Allow your Vercel frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes defined in router.py
app.include_router(router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "Backend is running"}

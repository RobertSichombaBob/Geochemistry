from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .endpoints import analyze
from .models import AnalysisResponse

app = FastAPI(
    title="Geochem Analytics API",
    description="Multivariate geochemical data analysis for mineral exploration.",
    version="1.0.0"
)

# CORS – allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Geochem Analytics API is running."}
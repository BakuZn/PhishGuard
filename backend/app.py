from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.analyze import router as analyze_router

app = FastAPI(
    title="PhishGuard Elite API",
    description="Multi-layered enterprise-grade phishing detection backend.",
    version="2.0.0"
)

# VERY IMPORTANT: Allow Chrome extension to communicate with this local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(analyze_router)

@app.get("/")
async def root():
    return {"message": "PhishGuard Elite Backend is running securely!"}

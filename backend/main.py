import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models

# Import routers
from routes import upload, predict, recommend, report, dashboard, map, history, chat

# Initialize database schemas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bengaluru Urban Heat Island Intelligence Platform API",
    description="Bengaluru climate intelligence, geospatial ML analytics, and smart city adaptation recommendation server",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(predict.router)
app.include_router(recommend.router)
app.include_router(report.router)
app.include_router(dashboard.router)
app.include_router(map.router)
app.include_router(history.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AI-Powered UHI Platform Backend",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

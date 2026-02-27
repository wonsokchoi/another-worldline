from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, characters, stories, rankings
from app.core.config import settings

app = FastAPI(
    title="다른 세계선 API",
    description="Another Worldline - AI 멀티버스 스토리 엔진",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(characters.router, prefix="/characters", tags=["characters"])
app.include_router(stories.router, prefix="/stories", tags=["stories"])
app.include_router(rankings.router, prefix="/rankings", tags=["rankings"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "another-worldline"}

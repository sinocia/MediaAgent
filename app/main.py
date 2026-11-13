from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.scoring import score_topic

app = FastAPI(title="AI Media Agent", version="0.1.0")

class TopicScoreRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    trend: float = Field(ge=0, le=10)
    audience_need: float = Field(ge=0, le=10)
    competition: float = Field(ge=0, le=10)
    monetization: float = Field(ge=0, le=10)
    weights: dict[str, float] | None = None

@app.get("/")
def root():
    return {"name": "AI Media Agent", "status": "starter",
            "note": "Publishing and data collection are not enabled by default."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/topics/score")
def topic_score(request: TopicScoreRequest):
    try:
        result = score_topic(trend=request.trend, audience_need=request.audience_need,
                             competition=request.competition, monetization=request.monetization,
                             weights=request.weights)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"title": request.title, **result}

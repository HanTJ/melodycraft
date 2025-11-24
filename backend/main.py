from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import analyze_prompt_raw
from config import get_allowed_origins
from music import generate_abc
from schemas import GenerateRequest, GenerateResponse

app = FastAPI(title="MelodyCraft API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "MelodyCraft API",
        "docs": "/docs",
        "usage": "POST /generate with prompt, measures?, seed?",
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    ai_hint = analyze_prompt_raw(req.prompt)
    result = generate_abc(
        req.prompt,
        req.measures,
        req.seed,
        ai_hint=ai_hint,
        instruments_requested=req.instruments,
    )
    highlights = [
        f"키: {result['key']}",
        f"템포: {result['tempo']} BPM",
        f"마디 수: {req.measures}",
        f"화성 진행: {' - '.join(result['progression'])}",
        f"파트: {', '.join([p['instrument'] for p in result['parts']])}",
        "프롬프트 기반 화성/멜로디 생성 (music21 검증 전 단계)",
    ]

    return GenerateResponse(
        abc=result["abc"],
        tempo=result["tempo"],
        meter=result["meter"],
        key=result["key"],
        mood=result["mood"],
        highlights=highlights,
        parts=result["parts"],
    )

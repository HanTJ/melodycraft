from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai import analyze_prompt_with_chatgpt
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
    ai_hint = analyze_prompt_with_chatgpt(req.prompt)
    result = generate_abc(
        req.prompt,
        req.measures,
        req.seed,
        ai_hint=ai_hint,
        instruments_requested=req.instruments,
    )
    return GenerateResponse(**result)

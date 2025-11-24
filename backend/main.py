import json
import os
import random
import re
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="사용자 프롬프트")
    measures: int = Field(4, ge=2, le=16, description="생성할 마디 수")
    seed: Optional[int] = Field(None, description="재현 가능한 결과를 위한 시드값")


class GenerateResponse(BaseModel):
    abc: str
    tempo: int
    meter: str
    key: str
    mood: str
    highlights: List[str]


MOOD_PROFILES = {
    "bright": {"keywords": ["밝", "신나", "happy", "fun", "경쾌"], "key": "C", "tempo": 118},
    "calm": {"keywords": ["잔잔", "calm", "편안", "휴식", "따뜻"], "key": "F", "tempo": 88},
    "dark": {"keywords": ["어둡", "dark", "서늘", "긴장", "긴박"], "key": "Am", "tempo": 96},
    "epic": {"keywords": ["장엄", "epic", "웅장", "모험", "영화"], "key": "G", "tempo": 132},
}

BASE_SCALE = ["C", "D", "E", "F", "G", "A", "B"]
HIGH_SCALE = ["c", "d", "e", "f", "g", "a", "b"]
PIANO_LOW = ["C", "D", "E", "F", "G", "A", "B", "C,", "D,", "E,"]

# .env 로컬 설정 로드 (없으면 무시)
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")


def pick_profile(prompt: str) -> str:
    lowered = prompt.lower()
    for mood, info in MOOD_PROFILES.items():
        for kw in info["keywords"]:
            if re.search(kw, lowered):
                return mood
    return "bright"


def normalize_mood(mood: Optional[str]) -> Optional[str]:
    if not mood:
        return None
    lowered = mood.lower()
    for key in MOOD_PROFILES.keys():
        if key in lowered:
            return key
    if "calm" in lowered or "soft" in lowered:
        return "calm"
    if "dark" in lowered or "tense" in lowered:
        return "dark"
    if "epic" in lowered or "grand" in lowered:
        return "epic"
    if "bright" in lowered or "happy" in lowered:
        return "bright"
    return None


def analyze_prompt_with_chatgpt(prompt: str):
    """
    ChatGPT API를 사용해 프롬프트에서 분위기/키/템포/마디를 추정합니다.
    - OPENAI_API_KEY 가 설정되지 않았거나 라이브러리가 없으면 None 반환
    - 실패 시에도 조용히 폴백하도록 설계
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "너는 음악 프롬프트를 해석해 멜로디 생성 파라미터를 제안하는 조력자야. "
        "아래 JSON 형식으로만 답해: "
        '{"mood":"bright|calm|dark|epic 중 하나 추천",'
        '"key":"예: C, G, Am",'
        '"tempo":숫자,'
        '"meter":"예: 4/4",'
        '"style":"피아노, 스트링 등 짧은 키워드"}'
        "피아노 연주곡 느낌을 우선 추천해."
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        content = completion.choices[0].message.content
        data = json.loads(content) if content else {}
        return {
            "mood": normalize_mood(data.get("mood")),
            "key": data.get("key"),
            "tempo": data.get("tempo"),
            "meter": data.get("meter"),
            "style": data.get("style"),
        }
    except Exception as e:
        # 실패해도 폴백으로 진행
        print(f"[chatgpt] prompt analysis failed: {e}")
        return None


def derive_seed(prompt: str, seed: Optional[int]) -> int:
    if seed is not None:
        return seed
    return abs(hash(prompt)) % (2**32)


def select_scale(key: str):
    # 간단화: 조성은 ABC 헤더에만 반영하고, 음 리스트는 공통 스케일로 사용
    return BASE_SCALE, HIGH_SCALE


def base_scale_for_key(key: str) -> List[str]:
    # 단순 메이저/내추럴 마이너 스케일 (플랫/샾은 간략화)
    natural = ["C", "D", "E", "F", "G", "A", "B"]
    start = key.replace("m", "")
    if start not in natural:
        return natural
    idx = natural.index(start)
    rotated = natural[idx:] + natural[:idx]
    if key.endswith("m"):
        # 자연단음계
        return rotated
    return rotated


def diatonic_chords(key: str, is_minor: bool) -> List[str]:
    scale = base_scale_for_key(key)
    if is_minor:
        # i ii° III iv v VI VII (간단화: ii는 m, v는 m, V는 장화음 선택 가능)
        return [
            f"{scale[0]}m",
            f"{scale[1]}m",
            scale[2],
            f"{scale[3]}m",
            scale[4],  # 느슨하게 V 메이저 처리
            scale[5],
            scale[6],
        ]
    # 메이저: I ii iii IV V vi vii°
    return [
        scale[0],
        f"{scale[1]}m",
        f"{scale[2]}m",
        scale[3],
        scale[4],
        f"{scale[5]}m",
        f"{scale[6]}dim",
    ]


def pick_progression(measures: int, mood: str, key: str, rng: random.Random) -> List[str]:
    is_minor = key.endswith("m")
    chords = diatonic_chords(key.replace("m", ""), is_minor)
    # 로마 숫자 진행 후보
    progressions = [
        ["I", "IV", "V", "I"],
        ["I", "vi", "IV", "V"],
        ["ii", "V", "I", "I"],
        ["I", "V", "vi", "IV"],
    ]
    if is_minor:
        progressions = [
            ["i", "VI", "III", "VII"],
            ["i", "iv", "V", "i"],
            ["i", "VI", "VII", "i"],
        ]
    if mood in ("calm", "dark"):
        progressions.append(["I", "iii", "vi", "IV"] if not is_minor else ["i", "v", "VI", "III"])
    selected = rng.choice(progressions)

    def roman_to_chord(roman: str) -> str:
        mapping = {
            "I": chords[0],
            "ii": chords[1] if len(chords) > 1 else chords[0],
            "iii": chords[2] if len(chords) > 2 else chords[0],
            "IV": chords[3] if len(chords) > 3 else chords[0],
            "V": chords[4] if len(chords) > 4 else chords[0],
            "vi": chords[5] if len(chords) > 5 else chords[0],
            "vii": chords[6] if len(chords) > 6 else chords[0],
            "i": chords[0] + "m" if not chords[0].endswith("m") else chords[0],
            "iv": chords[3] + "m" if len(chords) > 3 else chords[0],
        }
        # 대문자면 메이저, 소문자면 마이너 처리
        if roman not in mapping:
            return chords[0]
        chord = mapping[roman]
        # normalize dim -> m for simplicity
        if chord.endswith("dim"):
            return chord.replace("dim", "m")
        return chord

    seq = []
    for i in range(measures):
        chord = roman_to_chord(selected[i % len(selected)])
        seq.append(chord)
    return seq


def chord_note_pool(chord: str) -> List[str]:
    root = chord.replace("m", "")
    natural = ["C", "D", "E", "F", "G", "A", "B"]
    if root not in natural:
        root = "C"
    idx = natural.index(root)
    # 근음-3도-5도 선택
    third_idx = (idx + 2) % 7
    fifth_idx = (idx + 4) % 7
    third = natural[third_idx]
    fifth = natural[fifth_idx]
    if "m" in chord and len(third) == 1:
        # 단조면 3음 소문자 처리로 분리(음정 단순화)
        third = third.lower()
    low = [root, third.upper(), fifth]
    high = [root.lower(), third.lower(), fifth.lower()]
    return low + high


def build_measure(chord: str, scale_high: List[str], rng: random.Random) -> str:
    total_units = 0
    notes: List[str] = []
    chord_pool = chord_note_pool(chord)
    while total_units < 8:  # 4/4 기준, L:1/8 단위로 8칸
        length = rng.choice([1, 1, 2, 2, 1])
        if total_units + length > 8:
            length = 8 - total_units
        # 코드톤 중심 + 고음 스케일 섞기
        if rng.random() < 0.7:
            pitch = rng.choice(chord_pool)
        else:
            pitch = rng.choice(scale_high)
        note = pitch if length == 1 else f"{pitch}{length}"
        notes.append(note)
        total_units += length
    # 코드명을 첫 음에 표시
    if notes:
        notes[0] = f'"{chord}"{notes[0]}'
    return " ".join(notes)


def generate_abc(prompt: str, measures: int, seed: Optional[int]):
    ai_hint = analyze_prompt_with_chatgpt(prompt)
    profile_key = normalize_mood(ai_hint.get("mood") if ai_hint else None) or pick_profile(prompt)
    profile = MOOD_PROFILES[profile_key]
    rng = random.Random(derive_seed(prompt, seed))
    chosen_key = ai_hint.get("key") if ai_hint and ai_hint.get("key") else profile["key"]
    scale_low, scale_high = select_scale(chosen_key)
    # 피아노 스타일: 중저음도 조금 사용하도록 확장
    scale_low = PIANO_LOW

    progression = pick_progression(measures, profile_key, chosen_key, rng)
    intro = build_measure(progression[0], scale_high, rng)
    body = [build_measure(progression[i], scale_high, rng) for i in range(1, measures - 1)]
    ending = build_measure(progression[-1], scale_high, rng)

    meter = ai_hint.get("meter") if ai_hint and ai_hint.get("meter") else "4/4"
    tempo = ai_hint.get("tempo") if ai_hint and ai_hint.get("tempo") else profile["tempo"]
    key = chosen_key
    abc_body = " | ".join([intro] + body + [ending]) + " |]"
    abc_header = "\n".join(
        [
            "X:1",
            "T:MelodyCraft Sketch",
            f"M:{meter}",
            "L:1/8",
            f"Q:1/4={tempo}",
            f"K:{key}",
        ]
    )
    return {
        "abc": f"{abc_header}\n{abc_body}",
        "tempo": tempo,
        "meter": meter,
        "key": key,
        "mood": profile_key,
        "highlights": [
            f"키: {key}",
            f"템포: {tempo} BPM",
            f"마디 수: {measures}",
            f"분위기 감지: {profile_key}",
            f"화성 진행: {' - '.join(progression)}",
            "프롬프트 해석: ChatGPT 사용" if ai_hint else "프롬프트 해석: 기본 규칙 기반",
        ],
    }


app = FastAPI(title="MelodyCraft API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
    result = generate_abc(req.prompt, req.measures, req.seed)
    return GenerateResponse(**result)

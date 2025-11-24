import random
import re
from typing import Any, Dict, List, Optional

from config import get_openai_api_key

MOOD_PROFILES: Dict[str, Dict[str, Any]] = {
    "bright": {"keywords": ["밝", "신나", "happy", "fun", "경쾌"], "key": "C", "tempo": 118},
    "calm": {"keywords": ["잔잔", "calm", "편안", "휴식", "따뜻"], "key": "F", "tempo": 88},
    "dark": {"keywords": ["어둡", "dark", "서늘", "긴장", "긴박"], "key": "Am", "tempo": 96},
    "epic": {"keywords": ["장엄", "epic", "웅장", "모험", "영화"], "key": "G", "tempo": 132},
}

BASE_SCALE = ["C", "D", "E", "F", "G", "A", "B"]
HIGH_SCALE = ["c", "d", "e", "f", "g", "a", "b"]
PIANO_LOW = ["C", "D", "E", "F", "G", "A", "B", "C,", "D,", "E,"]

# 악기 설정: 음역/클레프
INSTRUMENT_SETTINGS = {
    "piano": {"clef": "treble", "octave_bias": 0, "program": 1},
    "strings": {"clef": "treble", "octave_bias": 1, "program": 49},
    "bass": {"clef": "bass", "octave_bias": -1, "program": 33},
    "guitar": {"clef": "treble", "octave_bias": -1, "program": 26},
    "flute": {"clef": "treble", "octave_bias": 1, "program": 74},
    "violin": {"clef": "treble", "octave_bias": 1, "program": 41},
    # contrabass 사운드폰트에 일부 음역 mp3 미존재 → cello를 string ensemble(49)로 매핑
    "cello": {"clef": "bass", "octave_bias": -2, "program": 49},
}


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
    return rotated


def diatonic_chords(key: str, is_minor: bool) -> List[str]:
    scale = base_scale_for_key(key)
    if is_minor:
        # i ii° III iv V VI VII (간단화: ii는 m, v는 m, V는 장화음 선택 가능)
        return [
            f"{scale[0]}m",
            f"{scale[1]}m",
            scale[2],
            f"{scale[3]}m",
            scale[4],
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

    roman_map = {
        "I": chords[0],
        "ii": chords[1] if len(chords) > 1 else chords[0],
        "iii": chords[2] if len(chords) > 2 else chords[0],
        "IV": chords[3] if len(chords) > 3 else chords[0],
        "V": chords[4] if len(chords) > 4 else chords[0],
        "vi": chords[5] if len(chords) > 5 else chords[0],
        "vii": chords[6] if len(chords) > 6 else chords[0],
        "i": chords[0] if chords[0].endswith("m") else f"{chords[0]}m",
        "iv": chords[3] if chords[3].endswith("m") else f"{chords[3]}m",
    }

    seq = []
    for i in range(measures):
        chord = roman_map.get(selected[i % len(selected)], chords[0])
        if chord.endswith("dim"):
            chord = chord.replace("dim", "m")
        seq.append(chord)
    return seq


def chord_note_pool(chord: str, octave_bias: int = 0) -> List[str]:
    root = chord.replace("m", "")
    natural = ["C", "D", "E", "F", "G", "A", "B"]
    if root not in natural:
        root = "C"
    idx = natural.index(root)
    third_idx = (idx + 2) % 7
    fifth_idx = (idx + 4) % 7
    third = natural[third_idx]
    fifth = natural[fifth_idx]
    if "m" in chord and len(third) == 1:
        third = third.lower()
    low = [root, third.upper(), fifth]
    high = [root.lower(), third.lower(), fifth.lower()]
    if octave_bias > 0:
        high = [n.lower() for n in high]  # 더 높은 옥타브
    if octave_bias < 0:
        low = [f"{n}," if n.isupper() else n for n in low]
    return low + high


def build_measure(chord: str, scale_high: List[str], rng: random.Random, octave_bias: int = 0) -> str:
    total_units = 0
    notes: List[str] = []
    chord_pool = chord_note_pool(chord, octave_bias=octave_bias)
    while total_units < 8:  # 4/4 기준, L:1/8 단위로 8칸
        length = rng.choice([1, 1, 2, 2, 1])
        if total_units + length > 8:
            length = 8 - total_units
        if rng.random() < 0.7:
            pitch = rng.choice(chord_pool)
        else:
            pitch = rng.choice(scale_high)
        note = pitch if length == 1 else f"{pitch}{length}"
        notes.append(note)
        total_units += length
    if notes:
        notes[0] = f'"{chord}"{notes[0]}'
    return " ".join(notes)


def resolve_profile(prompt: str, ai_hint: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    ai_mood = normalize_mood(ai_hint.get("mood") if ai_hint else None)
    profile_key = ai_mood or pick_profile(prompt)
    profile = MOOD_PROFILES[profile_key]
    key = ai_hint.get("key") if ai_hint and ai_hint.get("key") else profile["key"]
    meter = ai_hint.get("meter") if ai_hint and ai_hint.get("meter") else "4/4"
    tempo = ai_hint.get("tempo") if ai_hint and ai_hint.get("tempo") else profile["tempo"]
    return {"mood": profile_key, "key": key, "meter": meter, "tempo": tempo}


def generate_abc(
    prompt: str,
    measures: int,
    seed: Optional[int],
    ai_hint: Optional[Dict[str, Any]] = None,
    instruments_requested: Optional[List[str]] = None,
):
    rng = random.Random(derive_seed(prompt, seed))
    resolved = resolve_profile(prompt, ai_hint)

    scale_low, scale_high = select_scale(resolved["key"])
    scale_low = PIANO_LOW  # 피아노 스타일: 중저음 강조

    progression = pick_progression(measures, resolved["mood"], resolved["key"], rng)
    def build_part(instrument: str) -> str:
        settings = INSTRUMENT_SETTINGS.get(instrument, INSTRUMENT_SETTINGS["piano"])
        oct_bias = settings["octave_bias"]
        intro = build_measure(progression[0], scale_high, rng, octave_bias=oct_bias)
        body = [build_measure(progression[i], scale_high, rng, octave_bias=oct_bias) for i in range(1, measures - 1)]
        ending = build_measure(progression[-1], scale_high, rng, octave_bias=oct_bias)
        return " | ".join([intro] + body + [ending]) + " |]"

    def resolve_instruments(req_instruments: Optional[List[str]]) -> List[str]:
        if req_instruments:
            valid = [i for i in req_instruments if i in INSTRUMENT_SETTINGS]
            if valid:
                return valid
        return ["piano", "strings"]

    instruments = resolve_instruments(instruments_requested or (ai_hint.get("instruments") if ai_hint else None))

    parts: List[Dict[str, Any]] = []
    voice_bodies: List[str] = []
    voice_defs: List[str] = []
    midi_defs: List[str] = []
    for idx, inst in enumerate(instruments, start=1):
        part_body = build_part(inst)
        parts.append({"instrument": inst, "abc": part_body})
        settings = INSTRUMENT_SETTINGS.get(inst, INSTRUMENT_SETTINGS["piano"])
        # 간단한 GM 프로그램 매핑(1-base)
        program_map = {
            "piano": 1,
            "strings": 49,
            "bass": 33,
            "guitar": 26,
            "flute": 74,
            "violin": 41,
            "cello": 43,
        }
        program = program_map.get(inst, 1)
        # V 정의 + MIDI 채널/프로그램 지정 (abcjs에서 채널/프로그램을 인식하도록 헤더에 선언)
        channel = idx - 1  # 0-based channel
        voice_defs.append(f"V:{idx} clef={settings['clef']} name=\"{inst}\"")
        midi_defs.append(f"%%MIDI channel {idx} {channel}")
        midi_defs.append(f"%%MIDI program {idx} {program}")
        voice_bodies.append(f"[V:{idx}] {part_body}")

    abc_body = "\n".join(voice_bodies) + "\n|]"
    abc_header = "\n".join(
        [
            "X:1",
            "T:MelodyCraft Sketch",
            f"M:{resolved['meter']}",
            "L:1/8",
            f"Q:1/4={resolved['tempo']}",
            *midi_defs,
            f"K:{resolved['key']}",
            *voice_defs,
        ]
    )
    return {
        "abc": f"{abc_header}\n{abc_body}",
        "tempo": resolved["tempo"],
        "meter": resolved["meter"],
        "key": resolved["key"],
        "mood": resolved["mood"],
        "parts": parts,
        "highlights": [
            f"키: {resolved['key']}",
            f"템포: {resolved['tempo']} BPM",
            f"마디 수: {measures}",
            f"분위기 감지: {resolved['mood']}",
            f"화성 진행: {' - '.join(progression)}",
            f"파트: {', '.join(instruments)}",
            "프롬프트 해석: ChatGPT 사용" if ai_hint and get_openai_api_key() else "프롬프트 해석: 기본 규칙 기반",
        ],
    }

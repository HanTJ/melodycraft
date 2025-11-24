import json
from typing import Any, Dict, Optional

from config import get_openai_api_key, get_openai_model
from music import normalize_mood


def analyze_prompt_raw(prompt: str) -> Optional[Dict[str, Any]]:
    """
    ChatGPT에 프롬프트를 그대로 전달해 키/템포/미터/코드/악기 제안을 받는다.
    mood 기반 분류 없이 프롬프트 맥락을 그대로 사용.
    """
    api_key = get_openai_api_key()
    if not api_key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    model = get_openai_model()
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "너는 음악 프롬프트를 해석해 멜로디 생성 파라미터를 제안하는 조력자야. "
        "아래 JSON 형식으로만 답해: "
        '{"key":"예: C, G, Am",'
        '"tempo":숫자,'
        '"meter":"예: 4/4",'
        '"chords":["C","G","Am","F"],'
        '"instruments":["piano"]}'
    )

    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.4,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"{prompt}\n\n(마무리는 완결된 곡처럼 종결감을 주도록 부탁해.)",
                },
            ],
        )
        content = completion.choices[0].message.content
        data = json.loads(content) if content else {}
        return {
            "key": data.get("key"),
            "tempo": data.get("tempo"),
            "meter": data.get("meter"),
            "chords": data.get("chords"),
            "instruments": data.get("instruments"),
            "mood": normalize_mood(None),
        }
    except Exception as e:
        print(f"[chatgpt] prompt analysis failed: {e}")
        return None

import json
from typing import Any, Dict, Optional

from config import get_openai_api_key, get_openai_model
from music import normalize_mood


def analyze_prompt_with_chatgpt(prompt: str) -> Optional[Dict[str, Any]]:
    """
    ChatGPT API를 사용해 프롬프트에서 분위기/키/템포/마디/스타일을 추정합니다.
    - 환경 변수 OPENAI_API_KEY가 없거나 라이브러리를 사용할 수 없으면 None 반환
    - 실패 시 폴백: None 반환
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

# MelodyCraft Backend (FastAPI)

## 실행
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### ChatGPT 해석 연동(선택)
- `.env` 또는 환경 변수에 `OPENAI_API_KEY`를 설정하면 프롬프트를 ChatGPT 모델로 해석해 분위기/키/템포/마디를 추정하고 피아노 스타일로 보정합니다.
- 모델은 기본 `gpt-4o-mini`이며 `OPENAI_MODEL`로 변경 가능합니다.
- 키가 없거나 호출 실패 시 기존 규칙 기반 로직으로 폴백합니다.

## 엔드포인트
- `GET /` : 헬스/도움말
- `POST /generate`
  - 요청: `{ "prompt": "설명 텍스트", "measures": 4, "seed": 123 }`
  - 응답: `abc`(문자열), `tempo`, `meter`, `key`, `mood`, `highlights`

## 생성 로직
- (선택) ChatGPT로 프롬프트를 해석해 추천 mood/key/tempo/meter를 사용, 피아노 연주 스타일로 스케치.
- 프롬프트 키워드 기반 폴백 로직을 함께 사용해 안정적으로 결과 생성.
- 규칙 기반으로 4/4, L:1/8 단위 멜로디 생성 후 ABC notation 문자열 반환.
- 시드를 주면 동일 프롬프트에서 재현 가능한 결과를 얻을 수 있음.

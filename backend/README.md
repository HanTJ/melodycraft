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
  - 요청: `{ "prompt": "설명 텍스트", "measures": 4, "seed": 123, "instruments": ["piano","violin"] }`
  - 응답: `abc`(멀티 보이스 문자열), `tempo`, `meter`, `key`, `mood`, `highlights`, `parts`(악기별 ABC)

## 생성 로직
- (선택) ChatGPT로 프롬프트를 해석해 mood/key/tempo/meter 추천.
- 키워드 기반 폴백과 결합해 안정적으로 결과 생성.
- 화성 진행을 먼저 만들고, 악기별 파트(멀티 보이스)를 생성해 ABC를 합성.
- 시드를 주면 동일 프롬프트에서 재현 가능한 결과를 얻을 수 있음.

## 진행 상황 (멜로디/악기 협업)
- 여러 악기가 동시에 연주되는 멀티 보이스 ABC를 생성하도록 리팩토링 완료.
- cello 등 일부 음색은 사운드폰트 제약이 있어 string ensemble 등으로 매핑해 재생 안정성을 확보하는 중.
- 프론트와 연동하여 사용자가 악기 세트를 지정하면 해당 파트가 함께 생성/재생되도록 개발 진행 중.

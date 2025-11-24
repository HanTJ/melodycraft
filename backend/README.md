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
- `.env` 또는 환경 변수에 `OPENAI_API_KEY`를 설정하면 프롬프트를 그대로 보내 키/템포/미터/코드/악기를 제안받습니다.
- 모델은 기본 `gpt-4o-mini`이며 `OPENAI_MODEL`로 변경 가능합니다.
- 키가 없거나 호출 실패 시 기존 규칙 기반 로직으로 폴백합니다.

## 엔드포인트
- `GET /` : 헬스/도움말
- `POST /generate`
  - 요청: `{ "prompt": "설명 텍스트", "measures": 16, "seed": 123, "instruments": ["piano"] }`
    - `measures`: 2~64 (기본 16)
    - `instruments`: 단일 악기 선택을 권장(UI는 1개 선택)
  - 응답: `abc`(보이스 포함 문자열), `tempo`, `meter`, `key`, `mood`, `highlights`, `parts`(악기별 ABC)

## 생성 로직
- (선택) ChatGPT로 프롬프트를 해석해 key/tempo/meter/chords 추천(마무리 종결감 요청 포함).
- 키워드 기반 폴백과 결합해 화성 진행 → 마디별 코드톤 기반 멜로디를 생성한 뒤 ABC 합성.
- 시드를 주면 동일 프롬프트에서 재현 가능한 결과를 얻을 수 있음.

## 진행 상황 (멜로디/악기 협업)
- 여러 악기가 동시에 연주되는 멀티 보이스 ABC 지원(프론트는 현재 단일 악기 선택 UI).
- cello 등 일부 음색은 사운드폰트 제약이 있어 string ensemble 등으로 매핑해 재생 안정성을 확보하는 중.
- 음악21 기반 후처리는 일시 중단하고, 규칙 기반 화성/멜로디 생성에 집중 중. 프롬프트에는 곡 종결감을 요청하도록 전달.

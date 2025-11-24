# MelodyCraft

프롬프트(한국어)로 원하는 분위기의 음악을 요청하면 악보(ABC notation)를 생성하고 브라우저에서 재생까지 해주는 실험용 웹 앱입니다.

## 폴더 구조
- `backend/` : FastAPI 기반 생성 API
- `frontend/` : Next.js 기반 UI, abcjs로 악보/재생 처리
- `AGENTS.md` : 프로젝트 계획 및 결정 사항

## 빠른 실행
1) 백엔드
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
2) 프론트엔드
```bash
cd frontend
npm install
npm run dev
```
3) 브라우저에서 `http://localhost:3000` 접속 후 프롬프트 입력

## 기능 개요
- 프롬프트 분위기 분석 → 키/템포 선택 → 규칙 기반 멜로디 생성
- 결과: ABC notation 문자열, 키/템포/무드 메타데이터
- 프론트에서 악보 렌더링 및 Web Audio 재생

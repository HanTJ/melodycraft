# MelodyCraft 프로젝트 계획

## 목표
- 사용자가 한국어 프롬프트로 원하는 음악/장르/기분을 입력하면, 간단한 규칙 기반 생성기로 악보(ABC notation)를 만들고 재생 가능한 형태(MIDI/Audio)로 제공하는 웹 서비스 구축.
- 프론트엔드와 백엔드를 폴더로 완전히 분리하여 Next.js(프론트) + FastAPI(백엔드) 구조 확립.
- 생성 과정과 결과를 시각적으로(악보)와 청각적으로(재생) 확인할 수 있는 직관적 UI 제공.

## 요구사항 정리
- 모든 인터랙티브 대화는 한국어로 안내/표시.
- 폴더 구조: `frontend/`(Next.js)와 `backend/`(FastAPI)로 분리.
- 백엔드는 프롬프트를 받아 간단한 규칙 기반 멜로디 생성 → ABC notation 문자열과 메타데이터(JSON) 응답.
- 프론트는 프롬프트 입력, 생성 요청, 악보 렌더링, 재생 컨트롤 제공. (abcjs / Tone 기반)
- 프로젝트 진행 전에 본 계획을 작성하고 이후 구현 시작.

## 아키텍처 개요
- **Frontend (Next.js / TypeScript)**
  - 페이지: 단일 생성 페이지 (`/`)에서 프롬프트 입력, 생성 결과 표시.
  - 컴포넌트: PromptForm, ScoreViewer(ABC 렌더링), PlayerControls(재생).
  - 데이터 흐름: 사용자 프롬프트 → `/api/generate`(프록시 라우트) → FastAPI → 결과(ABC, tempo, meter) → abcjs로 렌더/재생.
- **Backend (FastAPI / Python)**
  - 엔드포인트: `POST /generate` (prompt, seed optional) → 규칙 기반 생성기 → ABC 문자열 및 메타 정보 반환.
  - 생성 로직: 프롬프트 토큰화 → 감정/에너지 추정 → 키/스케일/템포 선택 → 단순 패턴 시퀀스(tonic/med/subdom/dominant) 생성 → ABC 포맷 직렬화.
  - CORS 허용: localhost 개발용 허용.

## 개발 단계 플랜
1) 백엔드/프론트 폴더 스캐폴딩 생성, 기본 설정 파일 작성.
2) FastAPI 앱: 엔드포인트 구현, 규칙 기반 멜로디/리듬 생성기, 스키마(Pydantic) 정의, CORS 설정, 실행 스크립트.
3) Next.js 앱: 기본 페이지 + API 라우트(백엔드 프록시) + UI 컴포넌트(폼/악보뷰/플레이어), abcjs 로더 설정.
4) 상태 관리: 요청 진행 상태/에러 처리, “한국어” 안내 텍스트 적용.
5) 테스트/검증: 로컬 실행 안내, 예시 프롬프트/응답 확인, 문서화(README 섹션 또는 페이지 내 도움말).

## 산출물/문서
- `AGENTS.md`: 계획(본 문서) 및 추후 주요 결정 기록.
- 백엔드: `backend/main.py`, `backend/requirements.txt`, `backend/README.md`.
- 프론트: `frontend/` Next.js 구조, 주요 컴포넌트, 환경변수 예시(`.env.example`).
- 사용 안내: 실행 방법, API 설명, 예시 프롬프트/결과.

## 위험/대응
- 네트워크 없이 패키지 설치 불가 가능성 → 코드/구조만 작성, 실행 시 pacakge install 안내.
- 음악 생성 품질 제한 → 규칙 기반으로 단순 멜로디/리듬 제공, 추후 모델 교체 가능하도록 모듈화.
- 오디오 재생 브라우저 호환 → abcjs 기반으로 기본 재생, 실패 시 악보만 표시하도록 폴백 메시지 제공.

## 다음 작업
- 위 단계에 따라 스캐폴딩부터 구현 시작.

# MelodyCraft Frontend (Next.js)

## 실행
```bash
cd frontend
npm install
npm run dev
```

> 백엔드(FastAPI)가 `http://localhost:8000` 에서 실행 중인지 확인하세요. 다른 주소를 쓰려면 `.env.local`에 `NEXT_PUBLIC_API_BASE_URL`을 설정한 뒤 재시작합니다.

## 구조
- `app/page.tsx`: 메인 페이지(UI/상태)
- `app/api/generate/route.ts`: 백엔드 프록시 API
- `components/PromptForm.tsx`: 프롬프트 입력 폼
- `components/ScoreViewer.tsx`: abcjs로 악보 렌더링
- `components/PlayerControls.tsx`: abcjs Web Audio 재생
- `lib/api.ts`: 프론트 API 클라이언트

## 기능
- 프롬프트/마디 수/시드 입력 → 백엔드 호출 → ABC notation 수신
- 악기 다중 선택 → 멀티 보이스 ABC 생성(협업 연주 개발 중)
- abcjs로 악보 표시 및 재생(브라우저 오디오 권한 필요)
- ABC/MIDI 다운로드 기능 제공
- 전체 UI 한국어 안내

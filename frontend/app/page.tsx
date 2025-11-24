"use client";

import { useMemo, useState } from "react";
import { PromptForm } from "../components/PromptForm";
import { ScoreViewer } from "../components/ScoreViewer";
import { PlayerControls } from "../components/PlayerControls";
import { GenerateResponse, requestGenerate } from "../lib/api";

export default function Home() {
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (prompt: string, measures: number, seed?: number, instruments?: string[]) => {
    setLoading(true);
    setError(null);
    try {
      const data = await requestGenerate(prompt, measures, seed, instruments);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError("생성에 실패했습니다. 백엔드가 실행 중인지 확인하세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page">
      <header style={{ marginBottom: 20 }}>
        <p className="badge">MelodyCraft · Prompt-to-Score</p>
        <h1 className="title">
          🎹 멜로디를 만들어 보세요
        </h1>
        <p className="subtitle">
          프롬프트를 입력하면 규칙 기반 생성기가 간단한 악보와 재생 오디오를 만들어 줍니다.
        </p>
        <div className="chips">
          <span className="chip">FastAPI 백엔드</span>
          <span className="chip">Next.js 프론트</span>
          <span className="chip">ABC Notation + abcjs</span>
          <span className="chip">Seed 재현성</span>
        </div>
      </header>

      <div className="grid">
        <PromptForm onSubmit={handleSubmit} loading={loading} />
        <div className="card">
          <h2 className="title">🧭 진행 상태</h2>
          <p className="subtitle">생성 결과와 설정을 한눈에 확인하세요.</p>
          {loading && <div className="status">⏳ 악보를 생성하는 중...</div>}
          {error && <div className="status" style={{ color: "#ffbaba", border: "1px solid rgba(255,186,186,0.4)" }}>{error}</div>}
          {result ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div className="badge">분위기: {result.mood}</div>
              <div className="chips">
                <span className="chip">키: {result.key}</span>
                <span className="chip">템포: {result.tempo} BPM</span>
                <span className="chip">{result.meter}</span>
              </div>
              <ul style={{ paddingLeft: 18, color: "var(--muted)", margin: 0, lineHeight: 1.6 }}>
                {result.highlights.map((item, idx) => (
                  <li key={idx}>{item}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="muted">프롬프트를 입력하면 결과가 여기에 표시됩니다.</p>
          )}
        </div>
      </div>

      <div className="grid" style={{ marginTop: 18 }}>
        <ScoreViewer abc={result?.abc ?? null} parts={result?.parts ?? []} />
        <PlayerControls abc={result?.abc ?? null} />
      </div>
    </main>
  );
}

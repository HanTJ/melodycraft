"use client";

import { useState } from "react";

type PromptFormProps = {
  onSubmit: (prompt: string, measures: number, seed?: number, instruments?: string[]) => void;
  loading: boolean;
};

const INSTRUMENT_OPTIONS = ["piano", "strings", "bass", "guitar", "flute", "violin", "cello"];

export function PromptForm({ onSubmit, loading }: PromptFormProps) {
  const [prompt, setPrompt] = useState("잔잔하고 서정적인 클래식 피아노 소나타, 서서히 고조되다 마지막에 종결감 있게 마무리");
  const [measures, setMeasures] = useState(16);
  const [seed, setSeed] = useState<string>("");
  const [selectedInstruments, setSelectedInstruments] = useState<string[]>(["piano"]);

  const toggleInstrument = (inst: string) => {
    setSelectedInstruments((prev) =>
      prev.includes(inst) ? prev.filter((i) => i !== inst) : [...prev, inst]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const numericSeed = seed === "" ? undefined : Number(seed);
    onSubmit(prompt.trim(), measures, Number.isNaN(numericSeed) ? undefined : numericSeed, selectedInstruments);
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2 className="title">
        🎛️ 프롬프트 입력
      </h2>
      <p className="subtitle">어떤 분위기의 음악을 만들까요? 키워드를 적어주세요.</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <span className="muted">프롬프트</span>
          <textarea
            required
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="예) 몽환적이고 서정적인 일렉 피아노, 저녁 노을"
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: 12,
              padding: "12px 14px",
              color: "var(--text)",
              minHeight: 96,
              resize: "vertical",
              fontSize: 15,
            }}
          />
        </label>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12 }}>
          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="muted">마디 수 (2-64)</span>
            <input
              type="number"
              min={2}
              max={64}
              value={measures}
              onChange={(e) => setMeasures(Number(e.target.value))}
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 12,
                padding: "12px 14px",
                color: "var(--text)",
              }}
            />
          </label>
          <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <span className="muted">시드 (옵션)</span>
            <input
              type="number"
              placeholder="랜덤 고정용"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 12,
                padding: "12px 14px",
                color: "var(--text)",
              }}
            />
          </label>
        </div>
        <div>
          <span className="muted">연주 악기 선택(1개)</span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
            {INSTRUMENT_OPTIONS.map((inst) => {
              const active = selectedInstruments.includes(inst);
              return (
                <button
                  type="button"
                  key={inst}
                  onClick={() => setSelectedInstruments([inst])}
                  style={{
                    padding: "8px 12px",
                    borderRadius: 10,
                    border: active ? "1px solid #9be8ff" : "1px solid rgba(255,255,255,0.12)",
                    background: active ? "rgba(110,231,255,0.15)" : "rgba(255,255,255,0.05)",
                    color: active ? "#9be8ff" : "var(--text)",
                    cursor: "pointer",
                  }}
                >
                  {inst}
                </button>
              );
            })}
          </div>
        </div>
        <div className="actions">
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "12px 18px",
              borderRadius: 12,
              border: "none",
              background: "linear-gradient(135deg, #6ee7ff, #f472b6)",
              color: "#0b1021",
              fontWeight: 700,
              cursor: "pointer",
              boxShadow: "0 14px 40px rgba(94, 234, 212, 0.25)",
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? "생성 중..." : "생성하기"}
          </button>
        </div>
      </div>
    </form>
  );
}

"use client";

import { useEffect, useRef } from "react";
import { formatAbcByMeasures } from "../lib/abcFormat";

type Props = {
  abc: string | null;
  parts?: { instrument: string; abc: string }[];
};

export function ScoreViewer({ abc, parts = [] }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const formattedAbc = abc ? formatAbcByMeasures(abc, 4) : null;

  useEffect(() => {
    if (!formattedAbc || typeof window === "undefined") return;
    let isMounted = true;

    import("abcjs").then((mod) => {
      const abcjs = mod?.default ?? mod;
      if (!isMounted || !containerRef.current) return;
      containerRef.current.innerHTML = "";
      abcjs.renderAbc(containerRef.current, formattedAbc, {
        add_classes: true,
        scale: 1.1,
        responsive: "resize",
        wrap: { preferredMeasuresPerLine: 4 }, // 4마디씩 줄바꿈
      });
    });

    return () => {
      isMounted = false;
    };
  }, [formattedAbc]);

  const downloadText = (content: string, filename: string, mime = "text/plain") => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadAbc = () => {
    if (!formattedAbc) return;
    downloadText(formattedAbc, "melodycraft.abc");
  };

  const handleDownloadMidi = async () => {
    if (!formattedAbc) return;
    try {
      const mod = await import("abcjs");
      const abcjs = mod?.default ?? mod;
      const midiData = abcjs.synth.getMidiFile(formattedAbc, {
        midiOutputType: "encoded",
        fileName: "melodycraft.mid",
      });
      const href = Array.isArray(midiData) ? midiData[0] : midiData;
      const a = document.createElement("a");
      a.href = href;
      a.download = "melodycraft.mid";
      a.click();
    } catch (err) {
      console.error(err);
      alert("MIDI 내보내기에 실패했습니다.");
    }
  };

  return (
    <div className="card">
      <h2 className="title">🎼 생성된 악보</h2>
      <p className="subtitle">악보가 표시되지 않으면 ABC 텍스트를 복사해 별도 편집툴에 붙여보세요.</p>
      {formattedAbc && (
        <div className="actions" style={{ marginBottom: 10 }}>
          <button
            type="button"
            onClick={handleDownloadAbc}
            style={{
              padding: "8px 14px",
              borderRadius: 10,
              border: "1px solid rgba(255,255,255,0.14)",
              background: "rgba(110, 231, 255, 0.12)",
              color: "#9be8ff",
              cursor: "pointer",
            }}
          >
            ABC 다운로드
          </button>
          <button
            type="button"
            onClick={handleDownloadMidi}
            style={{
              padding: "8px 14px",
              borderRadius: 10,
              border: "1px solid rgba(255,255,255,0.14)",
              background: "rgba(244, 114, 182, 0.12)",
              color: "#ffdff1",
              cursor: "pointer",
            }}
          >
            MIDI 다운로드(실험)
          </button>
        </div>
      )}
      <div className="abc-container" ref={containerRef} />
      {formattedAbc && (
        <pre
          style={{
            marginTop: 12,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.08)",
            borderRadius: 12,
            padding: 12,
            color: "var(--muted)",
            whiteSpace: "pre-wrap",
            wordBreak: "break-all",
          }}
        >
          {formattedAbc}
        </pre>
      )}
      {!abc && <p className="muted">아직 생성된 악보가 없습니다.</p>}
    </div>
  );
}

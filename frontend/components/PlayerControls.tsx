"use client";

import { useEffect, useRef, useState } from "react";
import { formatAbcByMeasures } from "../lib/abcFormat";

type Props = {
  abc: string | null;
};

export function PlayerControls({ abc }: Props) {
  const [abcjs, setAbcjs] = useState<any>(null);
  const [visualObj, setVisualObj] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const synthRef = useRef<any>(null);
   const audioContextRef = useRef<AudioContext | null>(null);
  const hiddenRenderRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let mounted = true;
    import("abcjs")
      .then((mod) => {
        if (mounted) setAbcjs(mod?.default ?? mod);
      })
      .catch(() => {
        // audio/악보 지원이 없는 환경에서도 UI가 남도록 함
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!abc || !abcjs || !hiddenRenderRef.current) return;
    stopPlayback();
    const formatted = formatAbcByMeasures(abc, 4);
    const result = abcjs.renderAbc(hiddenRenderRef.current, formatted, {
      add_classes: true,
      wrap: { preferredMeasuresPerLine: 4 },
    });
    setVisualObj(result?.[0]);
    hiddenRenderRef.current.innerHTML = ""; // 화면에는 표시하지 않음
  }, [abc, abcjs]);

  const stopPlayback = () => {
    if (synthRef.current) {
      synthRef.current.stop();
      synthRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== "closed") {
      audioContextRef.current.close().catch(() => undefined);
    }
    audioContextRef.current = null;
    setIsPlaying(false);
  };

  const handlePlay = async () => {
    if (!abcjs || !visualObj) return;
    if (!abcjs.synth?.supportsAudio()) {
      alert("이 브라우저에서는 오디오 재생을 지원하지 않습니다. (Web Audio 미지원)");
      return;
    }
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioContext;
      await audioContext.resume();

      const synth = new abcjs.synth.CreateSynth();
      await synth.init({
        visualObj,
        audioContext,
        millisecondsPerMeasure: visualObj.millisecondsPerMeasure(),
        options: {
          // abcjs가 제공하는 공식 사운드폰트 CDN
          soundFontUrl: "https://paulrosen.github.io/midi-js-soundfonts/abcjs/",
          onEnded: stopPlayback,
        },
      });
      await synth.prime();
      synth.start();
      synthRef.current = synth;
      setIsPlaying(true);
    } catch (err) {
      console.error(err);
      stopPlayback();
    }
  };

  return (
    <div className="card">
      <h2 className="title">▶️ 재생 컨트롤</h2>
      <p className="subtitle">브라우저에서 Web Audio를 허용해야 소리가 납니다.</p>
      <div className="actions">
        <button
          type="button"
          onClick={handlePlay}
          disabled={!abc || isPlaying}
          style={{
            padding: "10px 16px",
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "rgba(110, 231, 255, 0.14)",
            color: "#9be8ff",
            cursor: abc ? "pointer" : "not-allowed",
          }}
        >
          재생
        </button>
        <button
          type="button"
          onClick={stopPlayback}
          disabled={!isPlaying}
          style={{
            padding: "10px 16px",
            borderRadius: 12,
            border: "1px solid rgba(255,255,255,0.12)",
            background: "rgba(244, 114, 182, 0.14)",
            color: "#ffdff1",
            cursor: isPlaying ? "pointer" : "not-allowed",
          }}
        >
          정지
        </button>
      </div>
      {!abc && <p className="muted" style={{ marginTop: 12 }}>아직 재생할 악보가 없습니다.</p>}
      <div ref={hiddenRenderRef} style={{ display: "none" }} />
    </div>
  );
}

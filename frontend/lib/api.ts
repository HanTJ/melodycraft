export type GenerateResponse = {
  abc: string;
  tempo: number;
  meter: string;
  key: string;
  mood: string;
  highlights: string[];
  parts: { instrument: string; abc: string }[];
};

export async function requestGenerate(
  prompt: string,
  measures = 4,
  seed?: number,
  instruments?: string[],
): Promise<GenerateResponse> {
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, measures, seed, instruments }),
  });

  if (!res.ok) {
    throw new Error("생성 요청에 실패했습니다.");
  }

  return res.json();
}

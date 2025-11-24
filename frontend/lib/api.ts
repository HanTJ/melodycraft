export type GenerateResponse = {
  abc: string;
  tempo: number;
  meter: string;
  key: string;
  mood: string;
  highlights: string[];
};

export async function requestGenerate(prompt: string, measures = 4, seed?: number): Promise<GenerateResponse> {
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, measures, seed }),
  });

  if (!res.ok) {
    throw new Error("생성 요청에 실패했습니다.");
  }

  return res.json();
}

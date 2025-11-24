import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export async function POST(request: Request) {
  const body = await request.json();
  const res = await fetch(`${API_BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    return NextResponse.json({ error: "생성에 실패했습니다." }, { status: 500 });
  }

  const data = await res.json();
  return NextResponse.json(data);
}

import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MelodyCraft",
  description: "프롬프트로 악보를 생성하고 재생하는 실험용 스케치",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}

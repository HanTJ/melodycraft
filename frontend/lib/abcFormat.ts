export function formatAbcByMeasures(abc: string, measuresPerLine = 4): string {
  if (!abc) return abc;

  const lines = abc.split("\n");
  const headerLines: string[] = [];
  const bodyLines: string[] = [];
  let bodyStarted = false;

  for (const line of lines) {
    if (!bodyStarted && line.includes("|")) {
      bodyStarted = true;
      bodyLines.push(line);
    } else if (bodyStarted) {
      bodyLines.push(line);
    } else {
      headerLines.push(line);
    }
  }

  const body = bodyLines.join(" ").trim();
  if (!body) return abc;

  let barCount = 0;
  let formattedBody = "";
  for (let i = 0; i < body.length; i++) {
    const ch = body[i];
    formattedBody += ch;
    if (ch === "|") {
      barCount += 1;
      if (barCount % measuresPerLine === 0) {
        formattedBody += "\n";
      }
    }
  }

  return [...headerLines, formattedBody].join("\n");
}

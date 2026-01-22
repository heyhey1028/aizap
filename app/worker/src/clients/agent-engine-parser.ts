/**
 * Agent Engine レスポンスの抽出ユーティリティ
 */

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

// Agent Engine のレスポンスは複数の形があるため、parts を共通抽出する。
const extractPartsFromCandidates = (candidates: unknown[]): unknown[] => {
  const parts: unknown[] = [];
  for (const candidate of candidates) {
    if (!isRecord(candidate)) continue;
    const candidateContent = candidate.content;
    if (isRecord(candidateContent) && Array.isArray(candidateContent.parts)) {
      parts.push(...candidateContent.parts);
    }
  }
  return parts;
};

const extractPartsFromContainer = (
  container: Record<string, unknown>
): unknown[] => {
  if (Array.isArray(container.parts)) {
    return container.parts;
  }
  const content = container.content;
  if (isRecord(content) && Array.isArray(content.parts)) {
    return content.parts;
  }
  const candidates = container.candidates;
  if (Array.isArray(candidates)) {
    return extractPartsFromCandidates(candidates);
  }
  return [];
};

const extractParts = (value: unknown): unknown[] => {
  if (!isRecord(value)) return [];
  const directParts = extractPartsFromContainer(value);
  if (directParts.length > 0) return directParts;

  // 代表的なコンテナを順番に探索する。
  for (const key of ['response', 'output', 'result'] as const) {
    const container = value[key];
    if (isRecord(container)) {
      const containerParts = extractPartsFromContainer(container);
      if (containerParts.length > 0) return containerParts;
    }
  }

  return [];
};

const FUNCTION_RESPONSE_TEXT_KEYS = [
  'message',
  'text',
  'report',
  'summary',
] as const;

const extractFunctionResponseText = (value: unknown): string[] => {
  if (!isRecord(value)) return [];
  const response = value.response;
  // function_response は文字列とオブジェクトの両方に対応する。
  if (typeof response === 'string') return [response];
  if (!isRecord(response)) return [];

  const candidates = FUNCTION_RESPONSE_TEXT_KEYS.map((key) => response[key])
    .filter((candidate): candidate is string => typeof candidate === 'string');

  if (candidates.length > 0) {
    return candidates;
  }
  return [JSON.stringify(response)];
};

export const extractTextValues = (value: unknown): string[] => {
  const parts = extractParts(value);
  if (parts.length === 0) return [];

  const texts: string[] = [];
  for (const part of parts) {
    if (!isRecord(part)) continue;
    if (typeof part.text === 'string') {
      texts.push(part.text);
      continue;
    }
    const functionResponse = part.function_response;
    if (isRecord(functionResponse)) {
      texts.push(...extractFunctionResponseText(functionResponse));
    }
  }
  return texts;
};

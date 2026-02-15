/**
 * Agent Engine streamQuery レスポンスから最終応答テキストを抽出する。
 *
 * 想定: サブエージェントはツールではなくサブエージェントとして呼び出される。
 * 応答はルートまたはいずれか1体のサブエージェントが直接出力するため、
 * 最終イベントのテキストのみを取得すればよい（function_response は参照しない）。
 *
 * streamQuery はイベント列（改行区切り JSON）を返すため、
 * ADK の is_final_response() 相当のロジックで最終イベントを判定する。
 *
 * @see https://google.github.io/adk-docs/events/
 * @see https://github.com/google/adk-python - Event.is_final_response()
 */

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

type EventLike = Record<string, unknown>;
type PartLike = Record<string, unknown>;

// Agent Engine のレスポンスは複数の形があるため、parts を共通抽出する。
const extractPartsFromCandidates = (candidates: unknown[]): PartLike[] => {
  const parts: PartLike[] = [];
  for (const candidate of candidates) {
    if (!isRecord(candidate)) continue;
    const candidateContent = candidate.content;
    if (isRecord(candidateContent) && Array.isArray(candidateContent.parts)) {
      parts.push(...(candidateContent.parts as PartLike[]));
    }
  }
  return parts;
};

const extractPartsFromContainer = (container: EventLike): PartLike[] => {
  if (Array.isArray(container.parts)) {
    return container.parts as PartLike[];
  }
  const content = container.content;
  if (isRecord(content) && Array.isArray(content.parts)) {
    return content.parts as PartLike[];
  }
  const candidates = container.candidates;
  if (Array.isArray(candidates)) {
    return extractPartsFromCandidates(candidates);
  }
  return [];
};

const extractParts = (value: unknown): PartLike[] => {
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
  'result',
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

  const candidates = FUNCTION_RESPONSE_TEXT_KEYS.map(
    (key) => response[key]
  ).filter((candidate): candidate is string => typeof candidate === 'string');

  if (candidates.length > 0) {
    return candidates;
  }
  return [JSON.stringify(response)];
};

const extractTextParts = (parts: PartLike[]): string[] =>
  parts
    .map((part) => (typeof part.text === 'string' ? part.text : null))
    .filter((text): text is string => text !== null);

const extractFunctionResponseParts = (parts: PartLike[]): string[] => {
  const responses: string[] = [];
  for (const part of parts) {
    const functionResponse = part.function_response;
    if (isRecord(functionResponse)) {
      responses.push(...extractFunctionResponseText(functionResponse));
    }
  }
  return responses;
};

const hasFunctionCalls = (parts: PartLike[]): boolean =>
  parts.some((part) => part.function_call !== undefined);

const hasFunctionResponses = (parts: PartLike[]): boolean =>
  parts.some((part) => part.function_response !== undefined);

const hasTrailingCodeExecutionResult = (parts: PartLike[]): boolean => {
  if (parts.length === 0) return false;
  const lastPart = parts[parts.length - 1];
  return lastPart.code_execution_result !== undefined;
};

const getSkipSummarization = (event: EventLike): boolean => {
  const actions = event.actions;
  if (!isRecord(actions)) return false;
  const skip = actions.skip_summarization ?? actions.skipSummarization;
  return skip === true;
};

const getLongRunningToolIds = (event: EventLike): unknown[] => {
  const ids =
    event.longRunningToolIds ??
    event.long_running_tool_ids ??
    event.longRunningToolIDs ??
    event.long_running_tool_IDs;
  return Array.isArray(ids) ? ids : [];
};

const isFinalResponseEvent = (event: EventLike): boolean => {
  const parts = extractParts(event);
  const isPartial = event.partial === true;
  if (getSkipSummarization(event) || getLongRunningToolIds(event).length > 0) {
    return true;
  }
  return (
    !hasFunctionCalls(parts) &&
    !hasFunctionResponses(parts) &&
    !isPartial &&
    !hasTrailingCodeExecutionResult(parts)
  );
};

const parseStreamEvents = (responseText: string): EventLike[] =>
  responseText
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) => {
      try {
        return JSON.parse(line) as unknown;
      } catch {
        return null;
      }
    })
    .filter((event): event is EventLike => isRecord(event));

export const extractFinalTextFromStream = (responseText: string): string => {
  const events = parseStreamEvents(responseText);
  let accumulatedText = '';
  let finalText: string | null = null;

  for (const event of events) {
    const parts = extractParts(event);
    const textParts = extractTextParts(parts);
    if (event.partial === true && textParts.length > 0) {
      accumulatedText += textParts.join('');
      continue;
    }
    if (!isFinalResponseEvent(event)) {
      continue;
    }

    if (textParts.length > 0) {
      finalText = `${accumulatedText}${textParts.join('')}`.trim();
      accumulatedText = '';
      continue;
    }

    const functionResponses = extractFunctionResponseParts(parts);
    if (functionResponses.length > 0) {
      finalText = functionResponses.join('\n').trim();
    }
  }

  return finalText ?? '';
};

/**
 * ルート／サブエージェントの構造化出力スキーマ（ADK output_schema に相当）。
 * プレーンテキストの場合は text のみ、JSON の場合は text と senderId を持つ。
 */
export type StructuredAgentReply = {
  text: string;
  senderId?: number;
};

/**
 * サブエージェント名 → senderId のマッピング。
 * schemas.py の senderId 定義と一致させる。
 */
const AGENT_SENDER_ID_MAP: Record<string, number> = {
  root_agent: 1,
  goal_setting_agent: 2,
  exercise_manager_agent: 3,
  meal_record_agent: 4,
};

/**
 * streamQuery のイベント列から応答エージェントの senderId を検出する。
 *
 * output_schema の senderId がテキストから取得できない場合の
 * フォールバックとして使用する。
 *
 * 検出方法（優先順）:
 * 1. 各イベントの author フィールド（ADK Event には必ず author が含まれる）
 *    から、最後にテキストを出力したエージェント名を取得する。
 *    2回目以降のリクエスト（既に transfer 済み）では transfer_to_agent が
 *    呼ばれないため、author ベースの検出が必要。
 * 2. transfer_to_agent の function_call から転送先エージェント名を取得する
 *    （初回 transfer 時のフォールバック）。
 *
 * @param responseText streamQuery のレスポンス全文
 * @returns 検出された senderId、見つからない場合は undefined
 */
export function detectSenderIdFromStream(
  responseText: string
): number | undefined {
  const events = parseStreamEvents(responseText);

  // 方法1: author フィールドから検出
  // ADK Event の author フィールドにエージェント名が入る。
  // 最終テキストイベントの author を使う。
  let lastTextAuthor: string | undefined;
  for (const event of events) {
    const author = event.author;
    if (typeof author !== 'string' || author.length === 0) continue;
    const parts = extractParts(event);
    const textParts = extractTextParts(parts);
    if (textParts.length > 0) {
      lastTextAuthor = author;
    }
  }
  if (lastTextAuthor && AGENT_SENDER_ID_MAP[lastTextAuthor] !== undefined) {
    return AGENT_SENDER_ID_MAP[lastTextAuthor];
  }

  // 方法2: transfer_to_agent の function_call から検出（フォールバック）
  let lastAgentName: string | undefined;
  for (const event of events) {
    const parts = extractParts(event);
    for (const part of parts) {
      const fc = part.function_call;
      if (
        isRecord(fc) &&
        fc.name === 'transfer_to_agent' &&
        isRecord(fc.args)
      ) {
        const args = fc.args as Record<string, unknown>;
        if (typeof args.agent_name === 'string') {
          lastAgentName = args.agent_name;
        }
      }
    }
  }

  return lastAgentName ? AGENT_SENDER_ID_MAP[lastAgentName] : undefined;
}

/**
 * 最終応答テキストを構造化レスポンスにパースする。
 * JSON で text と senderId を持つ場合は両方を返し、それ以外は text のみとする。
 *
 * @param raw 抽出された最終テキスト（プレーン or JSON 文字列）
 * @returns { text, senderId? }
 */
export function parseStructuredReply(raw: string): StructuredAgentReply {
  const trimmed = raw.trim();
  if (trimmed.length === 0) {
    return { text: '' };
  }
  try {
    const parsed = JSON.parse(trimmed) as unknown;
    if (
      parsed !== null &&
      typeof parsed === 'object' &&
      'text' in parsed &&
      typeof (parsed as { text: unknown }).text === 'string'
    ) {
      // senderId（camelCase）と sender_id（snake_case）の両方に対応
      // ADK の output_schema で Pydantic alias を設定していても、
      // LLM が snake_case で出力する場合がある
      const obj = parsed as {
        text: string;
        senderId?: number;
        sender_id?: number;
      };
      const rawSenderId = obj.senderId ?? obj.sender_id;
      const senderId =
        typeof rawSenderId === 'number' && Number.isFinite(rawSenderId)
          ? rawSenderId
          : undefined;
      return { text: obj.text, senderId };
    }
  } catch {
    // JSON でない場合はそのままテキストとして扱う。
  }
  return { text: trimmed };
}

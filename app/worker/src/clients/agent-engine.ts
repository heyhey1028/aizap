/**
 * Agent Engine REST API クライアント
 *
 * Vertex AI Agent Engine にデプロイされた ADK エージェントを呼び出す。
 */
import { GoogleAuth } from 'google-auth-library';
import { getProjectId, getRegion, getAgentEngineResourceId } from '@/config/env.js';
import { logger } from '@/utils/logger.js';

const JSON_HEADERS = { 'Content-Type': 'application/json' };

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const extractTextValues = (value: unknown): string[] => {
  if (!isRecord(value)) return [];
  const content = value.content;
  if (!isRecord(content)) return [];
  const parts = content.parts;
  if (!Array.isArray(parts)) return [];
  return parts
    .filter((part) => isRecord(part) && typeof part.text === 'string')
    .map((part) => part.text);
};

type CreateSessionResponse = {
  output: {
    id: string;
  };
};

type CreateSessionRequest = {
  class_method: 'async_create_session';
  input: {
    user_id: string;
  };
};

type StreamQueryRequest = {
  class_method: 'async_stream_query';
  input: {
    user_id: string;
    session_id: string;
    message: string;
  };
};

/**
 * Agent Engine クライアント
 */
export class AgentEngineClient {
  private auth: GoogleAuth;
  private projectId: string;
  private region: string;
  private resourceId: string;

  constructor() {
    this.auth = new GoogleAuth({
      scopes: ['https://www.googleapis.com/auth/cloud-platform'],
    });
    this.projectId = getProjectId();
    this.region = getRegion();
    this.resourceId = getAgentEngineResourceId();
  }

  /**
   * セッション操作用エンドポイント URL を取得（:query）
   *
   * @see https://google.github.io/adk-docs/deploy/agent-engine/test/
   */
  private getQueryEndpointUrl(): string {
    return `https://${this.region}-aiplatform.googleapis.com/v1/projects/${this.projectId}/locations/${this.region}/reasoningEngines/${this.resourceId}:query`;
  }

  /**
   * メッセージ送信用エンドポイント URL を取得（:streamQuery）
   *
   * @see https://google.github.io/adk-docs/deploy/agent-engine/test/
   */
  private getStreamQueryEndpointUrl(): string {
    return `https://${this.region}-aiplatform.googleapis.com/v1/projects/${this.projectId}/locations/${this.region}/reasoningEngines/${this.resourceId}:streamQuery`;
  }

  private buildCreateSessionRequest(userId: string): CreateSessionRequest {
    return {
      class_method: 'async_create_session',
      input: {
        user_id: userId,
      },
    };
  }

  private buildStreamQueryRequest(
    userId: string,
    sessionId: string,
    message: string
  ): StreamQueryRequest {
    return {
      class_method: 'async_stream_query',
      input: {
        user_id: userId,
        session_id: sessionId,
        message,
      },
    };
  }

  /**
   * セッションを作成する。
   *
   * @param userId ユーザー ID
   * @returns 作成されたセッション ID
   */
  async createSession(userId: string): Promise<string> {
    const client = await this.auth.getClient();
    const endpoint = this.getQueryEndpointUrl();

    logger.info({ userId }, 'Creating Agent Engine session');

    const response = await client.request<CreateSessionResponse>({
      url: endpoint,
      method: 'POST',
      data: this.buildCreateSessionRequest(userId),
      headers: JSON_HEADERS,
    });

    const sessionId = response.data.output.id;
    logger.info({ userId, sessionId }, 'Created Agent Engine session');
    return sessionId;
  }

  /**
   * Agent Engine にクエリを送信し、レスポンスを取得する。
   * sessionId が未指定の場合は新規セッションを作成する。
   *
   * @param userId ユーザー ID
   * @param sessionId セッション ID（未指定の場合は新規作成）
   * @param message ユーザーからのメッセージ
   * @returns エージェントからのレスポンステキスト
   */
  async query(userId: string, sessionId: string | undefined, message: string): Promise<string> {
    const client = await this.auth.getClient();

    const endpoint = this.getStreamQueryEndpointUrl();
    const resolvedSessionId = sessionId ?? (await this.createSession(userId));
    logger.info({ userId, sessionId: resolvedSessionId }, 'Querying Agent Engine');

    const response = await client.request<string>({
      url: endpoint,
      method: 'POST',
      data: this.buildStreamQueryRequest(userId, resolvedSessionId, message),
      headers: JSON_HEADERS,
      responseType: 'text',
    });

    const responseText = typeof response.data === 'string' ? response.data : JSON.stringify(response.data);
    return this.parseStreamResponse(responseText);
  }

  /**
   * 改行区切りレスポンスからテキストを抽出する。
   * streamQuery は SSE ではなく、改行区切り JSON を返す。
   *
   * @param responseText Agent Engine のレスポンス
   * @returns 抽出されたテキスト
   */
  private parseStreamResponse(responseText: string): string {
    const lines = responseText.split('\n').filter((line) => line.trim() !== '');
    const texts: string[] = [];

    for (const line of lines) {
      try {
        const parsed = JSON.parse(line) as unknown;
        texts.push(...extractTextValues(parsed));
      } catch (error) {
        logger.warn({ err: error }, 'Failed to parse Agent Engine event');
      }
    }

    if (texts.length === 0) {
      logger.warn('Agent Engine response has no text');
    }

    return texts.join('\n');
  }

  // --- SSE 利用時の参考実装（未使用） ---
  // private getSseEndpointUrl(): string {
  //   return `https://${this.region}-aiplatform.googleapis.com/v1/projects/${this.projectId}/locations/${this.region}/reasoningEngines/${this.resourceId}:query?alt=sse`;
  // }
  //
  // private buildSseRequestBody(userId: string, sessionId: string, message: string) {
  //   return {
  //     class_method: 'async_stream_query',
  //     input: {
  //       user_id: userId,
  //       session_id: sessionId,
  //       message,
  //     },
  //   };
  // }
  //
  // private parseSseResponse(sseResponse: string): string {
  //   const lines = sseResponse.split('\n');
  //   const texts: string[] = [];
  //
  //   for (const line of lines) {
  //     if (!line.startsWith('data: ')) continue;
  //     try {
  //       const parsed = JSON.parse(line.slice(6)) as unknown;
  //       texts.push(...extractTextValues(parsed));
  //     } catch (error) {
  //       // パース失敗はログに残してスキップ
  //       logger.warn({ err: error }, 'Failed to parse Agent Engine SSE event');
  //     }
  //   }
  //
  //   return texts.join('\n');
  // }
}

let agentEngineClient: AgentEngineClient | null = null;

/**
 * Agent Engine クライアントを取得する。
 * シングルトンパターンで、初回呼び出し時にインスタンスを生成する。
 *
 * @returns Agent Engine クライアント
 */
export function getAgentEngineClient(): AgentEngineClient {
  if (!agentEngineClient) {
    agentEngineClient = new AgentEngineClient();
  }
  return agentEngineClient;
}

/**
 * Pub/Sub Push エンドポイント
 *
 * Cloud Pub/Sub からのプッシュメッセージを受信し、
 * Agent Engine を呼び出して LINE に返信する。
 */
import { Hono } from 'hono';
import { logger } from '@/utils/logger.js';
import { decodeWebhookMessage, PubSubPushMessage } from '@/types/index.js';
import { getAgentEngineClient } from '@/clients/agent-engine.js';
import { uploadLineContent } from '@/clients/gcs.js';
import { getMessageContent, pushMessage } from '@/clients/line.js';

const api: Hono = new Hono();

/**
 * Pub/Sub Push ハンドラ
 *
 * 1. Pub/Sub メッセージをデコード
 * 2. Agent Engine にクエリを送信
 * 3. LINE Push API で返信
 */
api.post('/webhook', async (c) => {
  try {
    const body = (await c.req.json()) as PubSubPushMessage;
    const webhookMessage = decodeWebhookMessage(body.message.data);
    const userId = webhookMessage.userId;

    logger.info({ userId }, 'Received Pub/Sub message');

    const agentClient = getAgentEngineClient();
    // TODO: Prisma で userId と sessionId を永続化する。
    // - userId で sessionId を取得
    // - 無ければ createSession を実行して保存
    // - 以降は保存済み sessionId を利用
    if (webhookMessage.type === 'text') {
      const response = await agentClient.query(
        userId,
        webhookMessage.sessionId,
        webhookMessage.text
      );

      logger.info({ userId }, 'Got Agent Engine response');

      await pushMessage(userId, response);

      logger.info({ userId }, 'Webhook processed');
      return c.json({ status: 'success' }, 200);
    }

    if (
      webhookMessage.type === 'image' ||
      webhookMessage.type === 'video' ||
      webhookMessage.type === 'audio'
    ) {
      const { stream, contentType } = await getMessageContent(
        webhookMessage.messageId
      );
      const gcsUri = await uploadLineContent({
        userId,
        messageId: webhookMessage.messageId,
        messageType: webhookMessage.type,
        timestamp: webhookMessage.timestamp,
        contentType,
        stream,
      });

      let label = 'メディア';
      if (webhookMessage.type === 'image') {
        label = '画像';
      } else if (webhookMessage.type === 'video') {
        label = '動画';
      } else if (webhookMessage.type === 'audio') {
        label = '音声';
      }
      const message = `ユーザーが${label}を送信しました。 GCS: ${gcsUri}`;
      const response = await agentClient.query(
        userId,
        webhookMessage.sessionId,
        message
      );

      logger.info({ userId }, 'Got Agent Engine response');

      await pushMessage(userId, response);

      logger.info({ userId }, 'Webhook processed');
      return c.json({ status: 'success' }, 200);
    }

    logger.warn({ userId }, 'Unsupported message type');
    return c.json({ status: 'ignored' }, 200);
  } catch (error) {
    logger.error({ err: error }, 'Webhook error');

    if (error instanceof SyntaxError) {
      return c.json({ status: 'error', message: 'Invalid JSON' }, 200);
    }

    return c.json({ status: 'error' }, 500);
  }
});

export default api;

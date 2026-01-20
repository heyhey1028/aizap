/**
 * Pub/Sub Push エンドポイント
 *
 * Cloud Pub/Sub からのプッシュメッセージを受信し、
 * Agent Engine を呼び出して LINE に返信する。
 */
import { Hono } from 'hono';
import { logger } from '@/utils/logger.js';
import { decodeWebhookMessage, PubSubPushMessage } from '@/types/index.js';
import { getAgentEngineClient, Message } from '@/clients/agent-engine.js';
import { getPrismaClient } from '@/clients/prisma.js';
import { uploadLineContent, resolveContentType } from '@/clients/gcs.js';
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
    const prisma = getPrismaClient();

    // userId で sessionId を永続化して再利用する
    const storedSession = await prisma.userSession.findUnique({
      where: { userId },
    });
    const sessionId =
      storedSession?.sessionId ??
      webhookMessage.sessionId ??
      (await agentClient.createSession(userId));

    if (!storedSession) {
      await prisma.userSession.upsert({
        where: { userId },
        update: { sessionId },
        create: { userId, sessionId },
      });
      logger.info({ userId, sessionId }, 'Saved new session');
    }
    if (webhookMessage.type === 'text') {
      const response = await agentClient.query(
        userId,
        sessionId,
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

      const mimeType = resolveContentType(webhookMessage.type, contentType);
      const message: Message = {
        role: 'user',
        parts: [
          { text: `ユーザーが${label}を送信しました。` },
          { file_data: { file_uri: gcsUri, mime_type: mimeType } },
        ],
      };
      const response = await agentClient.query(userId, sessionId, message);

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

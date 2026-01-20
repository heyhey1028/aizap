import { Hono } from 'hono';
import type { WebhookEvent } from '@line/bot-sdk';
import { logger } from '@/utils/logger.js';
import { lineMiddleware } from '@/middleware/line.js';
import { getLineChannelSecret } from '@/config/env.js';
import { publishWebhookMessage } from '@/clients/pubsub.js';
import { replyMessage } from '@/clients/line.js';
import type { WebhookMessage } from '@/types/index.js';

/** スタンプ受信時の返信メッセージ */
const STICKER_REPLY_MESSAGE =
  'スタンプありがとう！テキスト、画像、音声、動画で話しかけてね 🎵';

const api: Hono = new Hono();

const handleEvent = async (event: WebhookEvent) => {
  if (event.type !== 'message') return;

  const userId = event.source.userId;
  if (!userId) return;

  if (event.message.type === 'text') {
    const message: WebhookMessage = {
      userId,
      replyToken: event.replyToken,
      messageId: event.message.id,
      type: 'text',
      text: event.message.text,
      timestamp: new Date(event.timestamp).toISOString(),
    };

    await publishWebhookMessage(message);
    return;
  }

  if (
    event.message.type === 'image' ||
    event.message.type === 'video' ||
    event.message.type === 'audio'
  ) {
    const message: WebhookMessage = {
      userId,
      replyToken: event.replyToken,
      messageId: event.message.id,
      type: event.message.type,
      timestamp: new Date(event.timestamp).toISOString(),
    };

    await publishWebhookMessage(message);
    return;
  }

  // スタンプは Agent Engine では処理できないため、即座に返信
  if (event.message.type === 'sticker') {
    logger.info({ userId }, 'Received sticker, replying with guidance message');
    await replyMessage(event.replyToken, STICKER_REPLY_MESSAGE);
    return;
  }

  // その他の未対応メッセージタイプはログのみ
  logger.warn(
    { userId, messageType: event.message.type },
    'Unsupported message type received'
  );
};

api.post(
  '/webhook',
  lineMiddleware({ channelSecret: getLineChannelSecret() }),
  async (c) => {
    try {
      const { events } = c.get('body');
      // eventsの配列が空の場合はLINEからのhealth checkのため早期リターン
      if (events.length === 0) {
        logger.info('Health check received');
        return c.json({ status: 'ok' }, 200);
      }

      await Promise.all(events.map(handleEvent));

      logger.info('Webhook received and processed successfully');
      return c.json({ status: 'success' }, 200);
    } catch (error) {
      logger.error({ err: error }, 'Webhook error');
      return c.json({ error: 'Internal Server Error' }, 500);
    }
  }
);

export default api;

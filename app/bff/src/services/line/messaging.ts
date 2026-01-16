import { getLineClient } from '@/infrastructure/line.js';

/**
 * テキストメッセージをオウム返しする。
 *
 * @param replyToken - LINE のリプライトークン
 * @param text - 返信するテキスト内容
 * @throws {Error} メッセージ送信に失敗した場合
 */
export async function echoTextMessage(
  replyToken: string,
  text: string
): Promise<void> {
  const client = getLineClient();

  await client.replyMessage(replyToken, {
    type: 'text',
    text: `reply: ${text}`,
  });
}

import { Sender } from '@line/bot-sdk';

export const RESET_MESSAGE =
  'セッションをリセットしました。続けて話しかけてください。';
export const RESET_PATTERN =
  /^(リセット|セッションリセット|最初から|はじめから|やり直し)(して|してください|お願い)?$/;
export const RESET_COMMANDS = new Set([
  'reset',
  'session reset',
  'session reset please',
]);
export const EMPTY_RESPONSE_MESSAGE =
  'すみません、現在応答を生成できませんでした。もう一度お試しください。';

export const getSender = (senderId: number): Sender | undefined => {
  // senderId は 2-4（1 は root agent のため送信元表示なし）
  if (senderId === 1 || senderId < 2 || senderId > 4) {
    return undefined;
  }

  const senders: Sender[] = [
    {
      name: '目標管理エージェント',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U016HKBBDDG-gd0fc4cab7e6-512',
    },
    {
      name: '食事前アドバイスエージェント',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U0134037W2V-2c7ce4babac6-512',
    },
    {
      name: '食事記録エージェント',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U030W6J3X28-fd2dfc14b5c8-512',
    },
  ];

  return senders[senderId - 2];
};

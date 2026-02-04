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
  // senderId は1-4までの整数
  if (senderId < 1 || senderId > 4) {
    return undefined;
  }

  const senders: Sender[] = [
    {
      name: 'Aizap',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U01F7L45V9B-7a1a1cde3347-512',
    },
    {
      name: 'わかなお',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U016HKBBDDG-gd0fc4cab7e6-512',
    },
    {
      name: 'miyasic',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U0134037W2V-2c7ce4babac6-512',
    },
    {
      name: 'heyhey',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U030W6J3X28-fd2dfc14b5c8-512',
    },
  ];

  return senders[senderId - 1];
};

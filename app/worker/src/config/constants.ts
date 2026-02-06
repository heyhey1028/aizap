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
  // senderId: 1=root, 2=goal_setting, 3=exercise_manager, 4=pre_meal_advisor, 5=meal_record
  if (senderId < 1 || senderId > 5) {
    return undefined;
  }

  const senders: Sender[] = [
    {
      name: 'a-zack',
      iconUrl: 'https://storage.googleapis.com/aizap-prod-asset/a-zack.png',
    }, // 1: root
    {
      name: '目標管理エージェント',
      iconUrl: 'https://storage.googleapis.com/aizap-prod-asset/goal-setting.png',
    }, // 2: goal_setting
    {
      name: 'a-burn',
      iconUrl: 'https://storage.googleapis.com/aizap-prod-asset/a-burn.png',
    }, // 3: exercise_manager
    {
      name: '食事前アドバイスエージェント',
      iconUrl:
        'https://ca.slack-edge.com/T012UQWDRQC-U0134037W2V-2c7ce4babac6-512',
    }, // 4: pre_meal_advisor
    {
      name: '食事記録エージェント',
      iconUrl:
        'https://storage.googleapis.com/aizap-prod-asset/food-advise.png',
    }, // 5: meal_record
  ];

  return senders[senderId - 1];
};

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

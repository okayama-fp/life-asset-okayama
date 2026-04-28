// =============================================
// Google Apps Script - LINE通知 + スプレッドシート記録
// =============================================
// 【使い方】
// 1. https://script.google.com にアクセス
// 2. 新しいプロジェクトを作成してこのコードを貼り付け
// 3. LINE_ACCESS_TOKEN と ADMIN_LINE_USER_ID を設定
// 4. 「デプロイ」→「新しいデプロイ」→「ウェブアプリ」で公開
// 5. 発行されたURLを index.html の GAS_URL に貼り付け
// =============================================

const LINE_ACCESS_TOKEN = 'ここにLINEチャネルアクセストークンを入力'; // ← 変更必須
const ADMIN_LINE_USER_ID = 'ここに管理者のLINEユーザーIDを入力';       // ← 変更必須

// フォーム送信を受け取る
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);

    // LINEに通知メッセージを送信
    const message =
      '【新規お問い合わせ】\n' +
      '━━━━━━━━━━━━\n' +
      'お名前: ' + data.name + '\n' +
      '電話番号: ' + (data.tel || '未入力') + '\n' +
      'メール: ' + data.email + '\n' +
      'ご相談内容: ' + (data.type || '未選択') + '\n' +
      '━━━━━━━━━━━━\n' +
      'メッセージ:\n' + (data.memo || 'なし');

    sendLineMessage(ADMIN_LINE_USER_ID, message);

    // スプレッドシートに記録
    saveToSheet(data);

    return ContentService
      .createTextOutput(JSON.stringify({ status: 'ok' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// LINE Push メッセージ送信
function sendLineMessage(userId, message) {
  const url = 'https://api.line.me/v2/bot/message/push';
  const payload = {
    to: userId,
    messages: [{ type: 'text', text: message }]
  };
  const options = {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN
    },
    payload: JSON.stringify(payload)
  };
  UrlFetchApp.fetch(url, options);
}

// スプレッドシートに記録（アクティブなシートに追記）
function saveToSheet(data) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // ヘッダーがなければ追加
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['日時', 'お名前', '電話番号', 'メール', 'ご相談内容', 'メッセージ']);
  }

  sheet.appendRow([
    new Date(),
    data.name  || '',
    data.tel   || '',
    data.email || '',
    data.type  || '',
    data.memo  || ''
  ]);
}

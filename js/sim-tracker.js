/**
 * sim-tracker.js — シミュレーター統計トラッカー
 *
 * 使い方（各シミュレーターから呼び出す）:
 *   trackToSheet('シミュレーター名', { key: 'value', ... });
 *
 * ・Cookie同意（la_cookie_consent=all）がある場合のみ動作
 * ・2秒デバウンス（スライダー連動型シミュレーター向け）
 * ・SHEET_URL を設定するとGoogleスプレッドシートにも記録
 */
(function () {
  /* ===== 設定 ===== */
  // Google Apps Script Web App URL（デプロイ後にここに貼り付ける）
  var SHEET_URL = 'https://script.google.com/macros/s/AKfycbxHsbyuNn0reGJRTDKywsRnxYsaPyKXgNuiDiNOMHMy3WqIhGCC88P4AeTOy18z0AMQ9A/exec';

  /* ===== 内部 ===== */
  var CONSENT_KEY = 'la_cookie_consent';
  var _timer = null;

  function hasConsent() {
    try { return localStorage.getItem(CONSENT_KEY) === 'all'; } catch (e) { return false; }
  }

  // スプレッドシートの数式インジェクション対策（2026-10-21）
  // = + - @ で始まる文字列はシートで数式として解釈されるため先頭に ' を付け、長さも制限する。
  // ※エンドポイントは公開されており直接POSTも可能なため、GAS側でも同じ検証を行うこと。
  function sanitize(obj) {
    var out = {};
    Object.keys(obj).slice(0, 30).forEach(function (k) {
      var v = obj[k];
      if (typeof v === 'string') {
        v = v.slice(0, 100);
        if (/^[=+\-@\t\r]/.test(v)) v = "'" + v;
      }
      out[String(k).slice(0, 40)] = v;
    });
    return out;
  }

  /**
   * シートに記録する（GA4は各シミュレーターに既存の gtag 呼び出しで対応）
   * @param {string} simName  シミュレーター識別子（例: 'lifeplan'）
   * @param {object} params   匿名化済みパラメータ（レンジ文字列・フラグ等）
   */
  window.trackToSheet = function (simName, params) {
    if (!SHEET_URL || !hasConsent()) return;
    clearTimeout(_timer);
    _timer = setTimeout(function () {
      try {
        fetch(SHEET_URL, {
          method: 'POST',
          // Content-Type を text/plain にすることで GAS の CORS プリフライトを回避
          headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
          body: JSON.stringify(
            sanitize(Object.assign({ sim: simName, ts: new Date().toISOString() }, params))
          )
        });
      } catch (_) {}
    }, 2000);
  };
})();

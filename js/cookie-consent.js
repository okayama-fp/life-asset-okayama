(function(){
  var KEY = 'la_cookie_consent';
  var GA_ID = 'G-PKDH2DR522';
  var ADS_CLIENT = 'ca-pub-1266918303152498';

  function loadScript(src, attrs) {
    var s = document.createElement('script');
    s.async = true;
    s.src = src;
    if (attrs) { Object.keys(attrs).forEach(function(k){ s.setAttribute(k, attrs[k]); }); }
    document.head.appendChild(s);
  }

  // 2026-10-21 修正:
  //  ・未同意時に disableTracking() が gtag を空関数にするため、初回同意時に
  //    config が送られずページビューが欠落していた → 必ず gtag を作り直す
  //  ・各ページの<head>のインライン gtag('config') と二重送信になっていた
  //    → キュー済みの js/config を取り除いてからここで1回だけ送る
  //  ・シミュレーターの共有URLは年収・資産額などをクエリに含むため、
  //    page_location からクエリとハッシュを除いて送る
  function enableAnalytics() {
    var q = window.dataLayer || [];
    window.dataLayer = [];
    for (var i = 0; i < q.length; i++) {
      var a = q[i];
      if (a && (a[0] === 'js' || a[0] === 'config')) continue;
      window.dataLayer.push(a);
    }
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window._gtag = window.gtag; // life-game.html などが参照
    window.gtag('js', new Date());
    window.gtag('config', GA_ID, {
      page_location: location.origin + location.pathname
    });
    loadScript('https://www.googletagmanager.com/gtag/js?id=' + GA_ID);
  }

  function enableAds() {
    loadScript('https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADS_CLIENT, {'crossorigin': 'anonymous'});
  }

  function disableTracking() {
    window.dataLayer = [];
    window.gtag = function(){};
  }

  function getConsent() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function setConsent(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }
  // プライバシーポリシーの「Cookie設定をリセット」から呼ぶ
  window.laResetCookieConsent = function() {
    try { localStorage.removeItem(KEY); } catch (e) {}
    location.reload();
  };

  var consent = getConsent();
  if (consent === 'all') {
    enableAnalytics();
    enableAds();
    return;
  }
  if (consent === 'none') {
    disableTracking();
    return;
  }

  // No consent yet — disable tracking until banner is answered
  disableTracking();

  function showBanner() {
    if (document.getElementById('la-cc')) return;
    var d = document.createElement('div');
    d.id = 'la-cc';
    d.innerHTML = '<style>'
      + '#la-cc{position:fixed;bottom:0;left:0;right:0;z-index:99999;background:#1a3d2b;color:#fff;padding:14px 20px;display:flex;align-items:center;gap:14px;flex-wrap:wrap;font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif;font-size:13px;line-height:1.6;box-shadow:0 -4px 20px rgba(0,0,0,.25)}'
      + '#la-cc p{flex:1;min-width:200px;margin:0;opacity:.9}'
      + '#la-cc a{color:#86efac;text-decoration:underline}'
      + '#la-cc-btns{display:flex;gap:8px;flex-shrink:0}'
      + '#la-cc-ok{background:#22c55e;color:#fff;border:none;border-radius:20px;padding:9px 20px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;white-space:nowrap}'
      + '#la-cc-ng{background:transparent;color:rgba(255,255,255,.7);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:9px 18px;font-size:13px;font-weight:700;cursor:pointer;font-family:inherit;white-space:nowrap}'
      + '@media(max-width:480px){#la-cc{flex-direction:column}#la-cc-btns{width:100%}#la-cc-ok,#la-cc-ng{flex:1;text-align:center}}'
      + '</style>'
      + '<p>当サイトではGoogle Analytics・広告配信のためにCookieを使用しています。詳細は<a href="/privacy.html">プライバシーポリシー</a>をご覧ください。</p>'
      + '<div id="la-cc-btns">'
      + '<button id="la-cc-ok">同意して続ける</button>'
      + '<button id="la-cc-ng">必要なもののみ</button>'
      + '</div>';
    document.body.appendChild(d);
    document.getElementById('la-cc-ok').onclick = function(){
      setConsent('all');
      d.remove();
      enableAnalytics();
      enableAds();
    };
    document.getElementById('la-cc-ng').onclick = function(){
      setConsent('none');
      d.remove();
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showBanner);
  } else {
    showBanner();
  }
})();

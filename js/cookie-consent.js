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

  function enableAnalytics() {
    loadScript('https://www.googletagmanager.com/gtag/js?id=' + GA_ID);
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function(){ window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }

  function enableAds() {
    loadScript('https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADS_CLIENT, {'crossorigin': 'anonymous'});
  }

  function disableTracking() {
    window.dataLayer = [];
    window.gtag = function(){};
  }

  var consent = localStorage.getItem(KEY);
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
      localStorage.setItem(KEY, 'all');
      d.remove();
      enableAnalytics();
      enableAds();
    };
    document.getElementById('la-cc-ng').onclick = function(){
      localStorage.setItem(KEY, 'none');
      d.remove();
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showBanner);
  } else {
    showBanner();
  }
})();

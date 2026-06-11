(function(){
  var btn = document.getElementById('hamburger');
  if (!btn) return;
  var hdr = btn.closest('header');
  btn.addEventListener('click', function() {
    var open = hdr.classList.toggle('nav-open');
    btn.setAttribute('aria-expanded', open);
  });
  document.addEventListener('click', function(e) {
    if (!hdr.contains(e.target)) {
      hdr.classList.remove('nav-open');
      btn.setAttribute('aria-expanded', 'false');
    }
  });

  /* ── モバイル用アコーディオンサブメニュー ── */
  var SUBMENUS = [
    {
      match: /simulation\.html/,
      items: [
        ['📈 資産・老後', '/simulation.html?cat=asset'],
        ['🎁 税制優遇', '/simulation.html?cat=tax'],
        ['🏠 住宅ローン', '/simulation.html?cat=loan'],
        ['🛡️ 保険・その他', '/simulation.html?cat=other'],
        ['💴 家計・収入', '/simulation.html?cat=income'],
        ['🎮 子ども学習', '/kids.html'],
        ['すべてのツールを見る →', '/simulation.html']
      ]
    },
    {
      match: /blog\/?(index\.html)?$/,
      items: [
        ['🏠 住宅ローン', '/blog/?cat=home'],
        ['📈 NISA・投資', '/blog/?cat=nisa'],
        ['💹 資産運用', '/blog/?cat=invest'],
        ['🏖️ 老後資金', '/blog/?cat=retire'],
        ['💴 家計管理', '/blog/?cat=kake'],
        ['🛡️ 保険', '/blog/?cat=hoken'],
        ['すべての記事を見る →', '/blog/']
      ]
    }
  ];

  var nav = hdr.querySelector('nav');
  if (!nav) return;

  Array.prototype.slice.call(nav.querySelectorAll('a')).forEach(function(link){
    var href = link.getAttribute('href') || '';
    var conf = null;
    for (var i = 0; i < SUBMENUS.length; i++) {
      if (SUBMENUS[i].match.test(href)) { conf = SUBMENUS[i]; break; }
    }
    if (!conf) return;

    var row = document.createElement('div');
    row.className = 'nav-sub-row';
    link.parentNode.insertBefore(row, link);
    row.appendChild(link);

    var toggle = document.createElement('button');
    toggle.className = 'nav-sub-toggle';
    toggle.setAttribute('aria-label', 'サブメニューを開く');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.innerHTML = '<span class="nav-sub-arrow"></span>';
    row.appendChild(toggle);

    var sub = document.createElement('div');
    sub.className = 'nav-sub';
    conf.items.forEach(function(item){
      var a = document.createElement('a');
      a.href = item[1];
      a.textContent = item[0];
      a.className = 'nav-sub-link';
      sub.appendChild(a);
    });
    row.parentNode.insertBefore(sub, row.nextSibling);

    toggle.addEventListener('click', function(e){
      e.stopPropagation();
      var open = sub.classList.toggle('open');
      toggle.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', open);
    });
  });
})();

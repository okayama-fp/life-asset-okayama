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
})();

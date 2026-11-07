// Playground shell: builds the sidebar from decisions.json. Ledger-driven —
// pages never hand-maintain their own history list.
(function () {
  var script = document.currentScript || document.querySelector('script[src*="playground-shell"]');
  var root = new URL('..', new URL(script.getAttribute('src'), location.href));

  fetch(new URL('decisions.json', root))
    .then(function (r) { return r.json(); })
    .then(function (ledger) {
      var entries = (ledger.entries || ledger || []).slice().reverse();
      var list = document.querySelector('.pg-history');
      if (!list) return;
      var here = location.pathname.split('/').pop().replace(/\.html$/, '');
      entries.forEach(function (e) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = new URL(e.url, root);
        if (e.url.split('/').pop().replace(/\.html$/, '') === here) a.className = 'pg-current';
        a.textContent = e.title;
        var d = document.createElement('span');
        d.className = 'pg-date';
        d.textContent = e.date + ' · ' + (e.section || '');
        a.appendChild(d);
        if (e.chosen) {
          var b = document.createElement('span');
          b.className = 'pg-chosen-badge';
          b.textContent = 'chose ' + e.chosen.toUpperCase();
          a.appendChild(b);
        }
        li.appendChild(a);
        list.appendChild(li);
      });
    })
    .catch(function (err) { console.warn('playground shell: could not load decisions.json', err); });
})();

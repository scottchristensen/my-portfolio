/* Theme toggle: system default, persisted manual override, no FOUC.
   The pre-paint snippet in each HTML <head> applies the class synchronously
   before paint; this file only wires the UI toggle and listeners. */
(function () {
  var STORAGE_KEY = 'theme';
  var root = document.documentElement;
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  function currentPref() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  function apply(pref) {
    var dark = pref === 'dark' || (pref !== 'light' && mq.matches);
    root.classList.toggle('theme-dark', dark);
  }

  function setPref(pref) {
    try {
      if (pref) localStorage.setItem(STORAGE_KEY, pref);
      else localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
    apply(pref);
  }

  // Follow system changes when the user hasn't picked an override.
  function onSystemChange() { if (!currentPref()) apply(null); }
  if (mq.addEventListener) mq.addEventListener('change', onSystemChange);
  else if (mq.addListener) mq.addListener(onSystemChange);

  function buildButton() {
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Toggle dark mode');
    btn.setAttribute('title', 'Toggle dark mode');
    btn.innerHTML =
      '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
        '<path d="M20.5 14.5A8 8 0 1 1 9.5 3.5a7 7 0 0 0 11 11Z" fill="currentColor"/>' +
      '</svg>' +
      '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" aria-hidden="true">' +
        '<circle cx="12" cy="12" r="4" fill="currentColor"/>' +
        '<g stroke="currentColor" stroke-width="1.75" stroke-linecap="round">' +
          '<path d="M12 3v2"/><path d="M12 19v2"/>' +
          '<path d="M3 12h2"/><path d="M19 12h2"/>' +
          '<path d="M5.6 5.6 7 7"/><path d="M17 17l1.4 1.4"/>' +
          '<path d="M5.6 18.4 7 17"/><path d="M17 7l1.4-1.4"/>' +
        '</g>' +
      '</svg>';
    btn.addEventListener('click', function () {
      var nextDark = !root.classList.contains('theme-dark');
      setPref(nextDark ? 'dark' : 'light');
    });
    return btn;
  }

  function insertToggle() {
    if (document.querySelector('.theme-toggle')) return;
    var container = document.querySelector('.nav-container');
    if (!container) return;
    var btn = buildButton();
    var menuBtn = container.querySelector('.menu-button');
    if (menuBtn) container.insertBefore(btn, menuBtn);
    else container.appendChild(btn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insertToggle);
  } else {
    insertToggle();
  }
})();

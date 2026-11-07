/* Theme: follows the OS light/dark setting automatically (no manual toggle).
   The pre-paint snippet in each HTML <head> applies the class synchronously
   before paint; this file keeps it in sync if the OS setting changes. */
(function () {
  var root = document.documentElement;
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  // Clear any override saved by the old manual toggle.
  try { localStorage.removeItem('theme'); } catch (e) {}

  function apply() { root.classList.toggle('theme-dark', mq.matches); }
  apply();

  if (mq.addEventListener) mq.addEventListener('change', apply);
  else if (mq.addListener) mq.addListener(apply);
})();

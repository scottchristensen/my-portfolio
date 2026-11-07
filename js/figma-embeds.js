// Click-to-load Figma embeds.
//
// Each Figma iframe boots a full WebGL Figma renderer (often 100MB+ of memory).
// A page with several of them can crash mobile Safari / low-memory tabs, and
// loading="lazy" doesn't help once you've scrolled past them — they stay alive.
//
// So embeds ship as a static facade (.figma-embed[data-figma-src]) and only get
// a real iframe when clicked. Only one embed is live at a time: loading a new
// one tears down the previous iframe, which actually frees its memory.
(function () {
  var active = null;

  function unload(wrapper) {
    var frame = wrapper.querySelector("iframe");
    if (frame) {
      frame.src = "about:blank";
      frame.remove();
    }
    wrapper.classList.remove("is-loaded");
  }

  function load(wrapper) {
    if (active && active !== wrapper) unload(active);
    if (wrapper.querySelector("iframe")) return;

    var frame = document.createElement("iframe");
    frame.src = wrapper.getAttribute("data-figma-src");
    frame.title = wrapper.getAttribute("data-figma-title") || "Figma embed";
    frame.setAttribute("allowfullscreen", "");
    wrapper.appendChild(frame);
    wrapper.classList.add("is-loaded");
    active = wrapper;
  }

  document.addEventListener("click", function (e) {
    // The poster screenshot is clickable too, not just the button.
    var btn = e.target.closest(".figma-embed__load, .figma-embed__poster");
    if (!btn) return;
    var wrapper = btn.closest(".figma-embed");
    if (wrapper) load(wrapper);
  });
})();

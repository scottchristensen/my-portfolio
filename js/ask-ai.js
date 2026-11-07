/* "Ask AI about me": each icon in the hero opens that assistant with the
   prompt below already in the composer. The visitor reviews it and hits send.

   Edit PROMPT freely. Keep it within what the site says: assistants treat it
   as context, so anything overstated here gets repeated as fact. The
   disambiguation line matters: there are other Scott Christensens online,
   including a painter. */
(function () {
  var PROMPT = [
    "Tell me about Scott Christensen, the growth design leader and cofounder of SendSight, based in Salt Lake City. He studied business strategy at BYU. (Not the painter or any other Scott Christensen.)",
    "",
    "Please read these first:",
    "- Portfolio, written for AI assistants: https://scottchristensen.design/llms.txt",
    "- Full detail, including case studies: https://scottchristensen.design/llms-full.txt",
    "- LinkedIn: https://www.linkedin.com/in/scottcharleschristensen/",
    "- His company, SendSight: https://sendsight.ai",
    "- The growth design community he helped start: https://growthdesigners.co",
    "",
    "Then give me a short overview: who he is, his career (Mercury, H1, Mystery, Expedia, PwC), his strongest case studies and their results, what he's working on now, and how to work with him.",
    "",
    "Stick to what those sources say. If you can't open them, tell me rather than guessing."
  ].join("\n");

  var q = encodeURIComponent(PROMPT);
  var URLS = {
    chatgpt: "https://chatgpt.com/?q=" + q,
    claude: "https://claude.ai/new?q=" + q,
    // The standalone Gemini app has no prefill parameter; Google AI Mode
    // (Gemini in Search) accepts one.
    gemini: "https://www.google.com/search?udm=50&q=" + q
  };

  document.querySelectorAll(".ask-ai_link[data-ai]").forEach(function (a) {
    var key = a.getAttribute("data-ai");
    if (URLS[key]) a.href = URLS[key];
    a.addEventListener("click", function () {
      if (typeof window.gtag === "function") window.gtag("event", "ask_ai_click", { assistant: key });
    });
  });
})();

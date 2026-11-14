// Loaded in <head> so the saved theme applies before first paint. Default is light.
(function () {
  var KEY = "artb-theme";
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  var q = /[?&]theme=(dark|light)\b/.exec(location.search);
  if (q) saved = q[1];
  if (saved === "dark") root.setAttribute("data-theme", "dark");

  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.querySelector(".theme");
    if (!btn) return;
    function sync() {
      var dark = root.getAttribute("data-theme") === "dark";
      btn.setAttribute("aria-pressed", dark ? "true" : "false");
    }
    sync();
    btn.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") !== "dark";
      if (dark) root.setAttribute("data-theme", "dark"); else root.removeAttribute("data-theme");
      try { localStorage.setItem(KEY, dark ? "dark" : "light"); } catch (e) {}
      sync();
    });
  });
})();

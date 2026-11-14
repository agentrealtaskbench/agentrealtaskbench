(function () {
  var LIMIT = 8;
  var buttons = document.querySelectorAll(".tabs button");
  var cards = Array.prototype.slice.call(document.querySelectorAll("#tgrid .tcard"));
  var more = document.getElementById("more");
  var filter = "all", expanded = false;
  function match(c) {
    if (filter === "all") return true;
    if (filter === "safety") return c.getAttribute("data-safety") === "1";
    return c.getAttribute("data-board") === filter;
  }
  function render() {
    var shown = 0, total = 0;
    cards.forEach(function (c) {
      var ok = match(c);
      if (ok) total++;
      c.hidden = !ok || (!expanded && shown >= LIMIT);
      if (ok && !c.hidden) shown++;
    });
    if (more) {
      more.hidden = total <= LIMIT;
      more.textContent = expanded ? more.getAttribute("data-less") : more.getAttribute("data-more") + " (" + total + ")";
    }
  }
  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      filter = btn.getAttribute("data-f");
      expanded = false;
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      render();
    });
  });
  if (more) more.addEventListener("click", function () { expanded = !expanded; render(); });
  render();
})();

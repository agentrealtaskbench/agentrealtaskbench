// Generic filter: <div class="tabs" data-filter="X"> buttons with data-f; items with data-item="X" data-tags="a b".
// A grid with data-for="X" data-limit="N" shows N items until its "show all" button is pressed.
(function () {
  document.querySelectorAll(".tabs[data-filter]").forEach(function (bar) {
    var name = bar.getAttribute("data-filter");
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-item="' + name + '"]'));
    var grid = document.querySelector('[data-for="' + name + '"]');
    var limit = grid ? parseInt(grid.getAttribute("data-limit") || "0", 10) : 0;
    var more = document.querySelector('[data-more-for="' + name + '"]');
    var filter = "all", expanded = false;
    function render() {
      var shown = 0, total = 0;
      items.forEach(function (el) {
        var tags = " " + (el.getAttribute("data-tags") || "") + " ";
        var ok = filter === "all" || tags.indexOf(" " + filter + " ") >= 0;
        if (ok) total++;
        var hide = !ok || (limit && !expanded && shown >= limit);
        el.hidden = hide;
        if (!hide) shown++;
      });
      if (more) {
        more.hidden = !limit || total <= limit;
        more.textContent = expanded ? more.getAttribute("data-less") : more.getAttribute("data-more") + " (" + total + ")";
      }
    }
    bar.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        filter = btn.getAttribute("data-f");
        expanded = false;
        bar.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
        render();
      });
    });
    if (more) more.addEventListener("click", function () { expanded = !expanded; render(); });
    render();
  });
})();

(function () {
  var buttons = document.querySelectorAll(".tabs button");
  var cards = document.querySelectorAll("#tgrid .tcard");
  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var f = btn.getAttribute("data-f");
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
      cards.forEach(function (c) {
        var show = f === "all" || (f === "safety" ? c.getAttribute("data-safety") === "1" : c.getAttribute("data-board") === f);
        c.hidden = !show;
      });
    });
  });
})();

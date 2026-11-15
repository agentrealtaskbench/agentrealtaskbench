(function () {
  var data = JSON.parse(document.getElementById("data").textContent);
  var A = document.getElementById("a"), B = document.getElementById("b"), out = document.getElementById("out");
  var L = data.labels;
  var ids = Object.keys(data.agents);
  var q = new URLSearchParams(location.search);
  A.value = q.get("a") && data.agents[q.get("a")] ? q.get("a") : ids[0];
  B.value = q.get("b") && data.agents[q.get("b")] ? q.get("b") : ids[Math.min(5, ids.length - 1)];

  function cell(v) {
    var td = document.createElement("td");
    if (v === null || v === undefined) { td.className = "blank"; td.textContent = L.blank; }
    else { td.className = "score"; td.textContent = typeof v === "number" ? v.toFixed(1) : v; }
    return td;
  }
  function row(label, a, b) {
    var tr = document.createElement("tr"), th = document.createElement("th");
    th.textContent = label; tr.appendChild(th); tr.appendChild(cell(a)); tr.appendChild(cell(b));
    out.appendChild(tr);
  }
  function setIcon(img, ag) {
    if (ag.icon) { img.src = ag.icon; img.hidden = false; } else { img.hidden = true; }
  }
  function render() {
    var a = data.agents[A.value], b = data.agents[B.value];
    setIcon(document.getElementById("ia"), a);
    setIcon(document.getElementById("ib"), b);
    out.textContent = "";
    var head = document.createElement("tr");
    [ "", a.name, b.name ].forEach(function (t) { var th = document.createElement("th"); th.textContent = t; head.appendChild(th); });
    out.appendChild(head);
    row(L.overall, a.overall, b.overall);
    row(L.safety, a.safety, b.safety);
    row(L.coverage, a.coverage + "/" + L.n_core, b.coverage + "/" + L.n_core);
    Object.keys(L.dims).forEach(function (d) { row(L.dims[d], a.dims[d], b.dims[d]); });
    history.replaceState(null, "", "?a=" + encodeURIComponent(A.value) + "&b=" + encodeURIComponent(B.value));
  }
  A.addEventListener("change", render);
  B.addEventListener("change", render);
  render();
})();

(function () {
  var langs = navigator.languages || [navigator.language || ""];
  var zh = langs.some(function (l) { return /^zh\b/i.test(l); });
  location.replace(zh ? "/zh/" : "/en/");
})();

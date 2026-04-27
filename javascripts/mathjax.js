(function () {
  var script = document.createElement("script");
  script.src = "https://polyfill.io/v3/polyfill.min.js?features=es6";
  document.head.appendChild(script);

  var mathJaxScript = document.createElement("script");
  mathJaxScript.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
  mathJaxScript.async = true;
  document.head.appendChild(mathJaxScript);
})();

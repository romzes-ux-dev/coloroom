/* ===== CURSOR START ===== */
(function () {
  "use strict";
  // ---- Настройки ----
  var CFG = {
    ringSize: 36,        // диаметр кольца, px
    ringHoverSize: 64,   // диаметр над ссылками/кнопками (= ringSize, чтобы отключить)
    dotSize: 6,          // диаметр точки
    ease: 0.18,          // инерция кольца (0..1; 1 = без инерции)
    interactive: "a, button, input, textarea, select, label, [role='button'], [data-cursor-hover]"
  };

  if (!window.matchMedia || window.matchMedia("(pointer: coarse)").matches) return;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // ---- Стили ----
  var style = document.createElement("style");
  style.textContent =
    "html.cc-on, html.cc-on *{cursor:none !important}" +
    ".cc-ring,.cc-dot{position:fixed; left:0; top:0; pointer-events:none; z-index:2147483647; border-radius:50%; opacity:0; transition:opacity .2s}" +
    ".cc-ring{width:var(--cc-size); height:var(--cc-size); margin:calc(var(--cc-size)/-2) 0 0 calc(var(--cc-size)/-2);" +
      "border:1.5px solid #fff; mix-blend-mode:difference; transition:width .25s, height .25s, margin .25s, background-color .25s, opacity .2s}" +
    ".cc-dot{width:" + CFG.dotSize + "px; height:" + CFG.dotSize + "px; margin:" + (-CFG.dotSize / 2) + "px 0 0 " + (-CFG.dotSize / 2) + "px; background:#fff; mix-blend-mode:difference}" +
    ".cc-visible .cc-ring,.cc-visible .cc-dot{opacity:1}" +
    ".cc-hover .cc-ring{background-color:rgba(255,255,255,.18)}";
  document.head.appendChild(style);

  // ---- Элементы ----
  var root = document.documentElement;
  var ring = document.createElement("div"); ring.className = "cc-ring";
  var dot = document.createElement("div"); dot.className = "cc-dot";
  ring.style.setProperty("--cc-size", CFG.ringSize + "px");
  document.body.append(ring, dot);
  root.classList.add("cc-on");

  var mx = -100, my = -100, rx = -100, ry = -100;

  document.addEventListener("pointermove", function (e) {
    if (e.pointerType === "touch") return;
    mx = e.clientX; my = e.clientY;
    dot.style.transform = "translate3d(" + mx + "px," + my + "px,0)";
    if (!root.classList.contains("cc-visible")) { root.classList.add("cc-visible"); rx = mx; ry = my; }
  }, { passive: true });

  document.addEventListener("mouseover", function (e) {
    var hover = !!(e.target.closest && e.target.closest(CFG.interactive));
    root.classList.toggle("cc-hover", hover);
    ring.style.setProperty("--cc-size", (hover ? CFG.ringHoverSize : CFG.ringSize) + "px");
  });
  document.addEventListener("mouseleave", function () { root.classList.remove("cc-visible"); });

  (function loop() {
    var k = reduce ? 1 : CFG.ease;
    rx += (mx - rx) * k; ry += (my - ry) * k;
    ring.style.transform = "translate3d(" + rx + "px," + ry + "px,0)";
    requestAnimationFrame(loop);
  })();
})();
/* ===== CURSOR END ===== */

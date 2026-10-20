/* Слайдер проектов на главной.
   Переход описывается одним числом p от 0 до 1: им управляют и автосмена, и перетаскивание.
   Параллакс — три слоя с разной скоростью: маска кадра, изображение (отстаёт), заголовок (обгоняет изображение). */
(function () {
  var root = document.querySelector('[data-slider]');
  if (!root) return;
  var slides = Array.prototype.slice.call(root.querySelectorAll('[data-slide]'));
  var N = slides.length;
  if (N < 2) return;

  var DELAY = 6000;      // пауза между слайдами, мс
  var DURATION = 1250;   // длительность перехода, мс
  var SHIFT = 0.18;      // сдвиг изображения, доля ширины слайдера (в CSS у .pslide__media запас 20%)

  var tabs = Array.prototype.slice.call(root.querySelectorAll('[data-idx]'));
  var count = root.querySelector('[data-count]');
  var toggle = root.querySelector('[data-toggle]');
  var parts = slides.map(function (s) {
    return { el: s, media: s.querySelector('.pslide__media'), cap: s.querySelector('.pslide__caption'), dim: s.querySelector('.pslide__dim') };
  });

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = 0, to = null, dir = 1, p = 0, raf = 0, elapsed = 0, playing = !reduced, hover = false, drag = null;

  function clamp(v) { return Math.min(1, Math.max(0, v)); }
  function ease(k) { return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function clear(o) {
    o.el.style.clipPath = o.el.style.webkitClipPath = o.el.style.opacity = o.el.style.zIndex = '';
    o.media.style.transform = o.cap.style.transform = o.cap.style.opacity = o.dim.style.opacity = '';
  }

  function paint() {
    parts.forEach(function (o, i) {
      var on = i === cur || i === to;
      o.el.classList.toggle('is-on', on);
      if (!on || to === null) clear(o);
    });
    if (to === null) return;
    var a = parts[cur], b = parts[to], w = root.clientWidth, rest = (1 - p) * 100;
    a.el.style.zIndex = 1;
    b.el.style.zIndex = 2;
    if (reduced) { b.el.style.opacity = p; return; }   // без движения: простое проявление
    var clip = dir > 0 ? 'inset(0 0 0 ' + rest + '%)' : 'inset(0 ' + rest + '% 0 0)';
    b.el.style.clipPath = b.el.style.webkitClipPath = clip;
    b.media.style.transform = 'translate3d(' + (dir * (1 - p) * w * SHIFT) + 'px,0,0)';
    b.cap.style.transform = 'translate3d(' + (dir * (1 - p) * w * 0.14) + 'px,0,0)';
    b.cap.style.opacity = clamp((p - 0.3) / 0.6);
    a.media.style.transform = 'translate3d(' + (-dir * p * w * SHIFT) + 'px,0,0)';
    a.cap.style.transform = 'translate3d(' + (-dir * p * w * 0.07) + 'px,0,0)';
    a.cap.style.opacity = clamp(1 - p * 2.2);
    a.dim.style.opacity = p * 0.45;
  }

  function sync() {
    slides.forEach(function (s, i) {
      s.classList.toggle('is-active', i === cur);
      s.inert = i !== cur;
    });
    tabs.forEach(function (t, i) {
      t.setAttribute('aria-current', i === cur ? 'true' : 'false');
      if (i !== cur) t.style.setProperty('--f', 0);
    });
    if (count) count.textContent = pad(cur + 1) + ' / ' + pad(N);
  }

  function run(target, ms) {
    window.cancelAnimationFrame(raf);
    var p0 = p, t0 = window.performance.now();
    (function step(now) {
      var k = clamp((now - t0) / ms);
      p = p0 + (target - p0) * ease(k);
      paint();
      if (k < 1) { raf = window.requestAnimationFrame(step); return; }
      if (target === 1) cur = to;
      to = null; p = 0; elapsed = 0;
      sync(); paint();
    })(t0);
  }

  function go(n, d) {
    if (to !== null) return;
    n = (n + N) % N;
    if (n === cur) return;
    to = n; dir = d; p = 0;
    run(1, reduced ? 350 : DURATION);
  }

  /* автосмена и полоска прогресса у активного проекта */
  var last = window.performance.now();
  (function tick(now) {
    var dt = now - last; last = now;
    if (playing && to === null && !hover && !drag && !document.hidden) {
      elapsed += dt;
      if (elapsed >= DELAY) { elapsed = 0; go(cur + 1, 1); }
    }
    if (tabs[cur]) tabs[cur].style.setProperty('--f', playing ? clamp(elapsed / DELAY) : 1);
    window.requestAnimationFrame(tick);
  })(last);

  /* управление */
  var next = root.querySelector('[data-next]'), prev = root.querySelector('[data-prev]');
  if (next) next.addEventListener('click', function () { go(cur + 1, 1); });
  if (prev) prev.addEventListener('click', function () { go(cur - 1, -1); });
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { go(i, i > cur ? 1 : -1); });
  });

  function setPlay(v) {
    playing = v; elapsed = 0;
    if (!toggle) return;
    toggle.setAttribute('aria-label', v ? 'Остановить автосмену' : 'Запустить автосмену');
    toggle.querySelector('path').setAttribute('d', v ? 'M9 6v12M15 6v12' : 'M8.5 5.5v13l10-6.5z');
  }
  if (toggle) toggle.addEventListener('click', function () { setPlay(!playing); });
  setPlay(playing);

  root.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hover = true; });
  root.addEventListener('pointerleave', function () { hover = false; });
  root.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(cur + 1, 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(cur - 1, -1); }
  });

  /* перетаскивание мышью и свайп */
  root.addEventListener('pointerdown', function (e) {
    if (to !== null || e.button > 0 || e.target.closest('button,a')) return;
    drag = { x: e.clientX, id: e.pointerId, on: false };
  });
  root.addEventListener('pointermove', function (e) {
    if (!drag || e.pointerId !== drag.id) return;
    var dx = e.clientX - drag.x;
    if (!drag.on) {
      if (Math.abs(dx) < 10) return;
      drag.on = true;
      root.classList.add('is-drag');
      try { root.setPointerCapture(drag.id); } catch (err) {}
    }
    var d = dx < 0 ? 1 : -1;
    if (to === null || d !== dir) { dir = d; to = (cur + d + N) % N; }
    p = clamp(Math.abs(dx) / root.clientWidth * 1.15);
    paint();
  });
  function release(e) {
    if (!drag || e.pointerId !== drag.id) return;
    var was = drag.on;
    drag = null;
    root.classList.remove('is-drag');
    if (!was || to === null) return;
    if (p > 0.18) run(1, 350 + 650 * (1 - p)); else run(0, 380);
  }
  root.addEventListener('pointerup', release);
  root.addEventListener('pointercancel', release);
  root.addEventListener('dragstart', function (e) { e.preventDefault(); });
  window.addEventListener('resize', paint);

  sync();
  paint();
})();

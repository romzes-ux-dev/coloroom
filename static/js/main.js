(function () {
  var burger = document.querySelector('.burger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = document.body.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* Прозрачная шапка над баннером становится плотной после прокрутки */
  var overlay = document.querySelector('.header--overlay');
  if (overlay) {
    var onScroll = function () { overlay.classList.toggle('is-scrolled', window.scrollY > 40); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ---------- Параллакс ---------- */
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = [];
  var ticking = false;
  var MAX_SHIFT = 0.12; // доля высоты рамки: картинка заходит за рамку на 12% сверху и снизу

  function collect() {
    items = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  }

  function update() {
    var vh = window.innerHeight;
    for (var i = 0; i < items.length; i++) {
      var el = items[i];
      var frame = el.parentElement;
      var r = frame.getBoundingClientRect();
      if (r.bottom < -150 || r.top > vh + 150) continue;
      var strength = parseFloat(el.getAttribute('data-parallax')) || 0.5;
      var y;
      if (el.getAttribute('data-mode') === 'hero') {
        // баннер уезжает медленнее страницы
        y = Math.min(window.scrollY * strength, r.height * 0.3);
      } else {
        // -1 (рамка внизу экрана) ... 1 (рамка вверху экрана)
        var p = (r.top + r.height / 2 - vh / 2) / (vh / 2 + r.height / 2);
        p = Math.max(-1, Math.min(1, p));
        y = -p * strength * MAX_SHIFT * r.height;
      }
      el.style.transform = 'translate3d(0,' + y.toFixed(1) + 'px,0)';
    }
    ticking = false;
  }

  function request() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(update);
    }
  }

  if (!reduce) {
    collect();
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    window.addEventListener('load', update);
    update();
  }

  // после подгрузки новых карточек пересчитываем список параллакс-картинок
  document.addEventListener('coloroom:content', function () {
    if (reduce) return;
    collect();
    update();
  });

  /* ---------- Каталог проектов: фильтры и «Загрузить ещё» без перезагрузки страницы ---------- */
  var root = document.querySelector('[data-projects]');
  if (!root || !window.fetch || !window.URLSearchParams || !window.FormData) return;

  var form = root.querySelector('.filters');
  var results = root.querySelector('[data-results]');
  var reset = root.querySelector('[data-reset]');
  if (!form || !results) return;

  function fetchDoc(url) {
    return fetch(url, { headers: { 'X-Requested-With': 'fetch' } })
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.text();
      })
      .then(function (text) {
        return new DOMParser().parseFromString(text, 'text/html');
      });
  }

  function hasFilters() {
    var year = form.querySelector('select[name="year"]');
    return !!form.querySelector('input:checked') || !!(year && year.value);
  }

  function refresh() {
    var params = new URLSearchParams(new FormData(form));
    if (!params.get('year')) params.delete('year');
    var qs = params.toString();
    var url = form.getAttribute('action') + (qs ? '?' + qs : '');
    results.classList.add('is-loading');
    fetchDoc(url)
      .then(function (doc) {
        var next = doc.querySelector('[data-results]');
        if (!next) throw new Error('no results');
        results.innerHTML = next.innerHTML;
        results.classList.remove('is-loading');
        if (reset) reset.classList.toggle('is-active', !hasFilters());
        window.history.replaceState(null, '', url);
        document.dispatchEvent(new Event('coloroom:content'));
      })
      .catch(function () {
        window.location.href = url;
      });
  }

  form.addEventListener('change', refresh);
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    refresh();
  });

  if (reset) {
    reset.addEventListener('click', function () {
      form.querySelectorAll('input:checked').forEach(function (i) { i.checked = false; });
      var year = form.querySelector('select[name="year"]');
      if (year) year.value = '';
      refresh();
    });
  }

  results.addEventListener('click', function (e) {
    var link = e.target.closest('[data-load-more]');
    if (!link) return;
    e.preventDefault();
    link.style.opacity = '0.5';
    fetchDoc(link.href)
      .then(function (doc) {
        var next = doc.querySelector('[data-results]');
        var grid = results.querySelector('[data-grid]');
        var more = results.querySelector('[data-more]');
        next.querySelectorAll('[data-grid] > *').forEach(function (n) {
          grid.appendChild(document.importNode(n, true));
        });
        var nextMore = next.querySelector('[data-more]');
        if (nextMore) more.replaceWith(document.importNode(nextMore, true));
        else if (more) more.remove();
        document.dispatchEvent(new Event('coloroom:content'));
      })
      .catch(function () {
        window.location.href = link.href;
      });
  });
})();

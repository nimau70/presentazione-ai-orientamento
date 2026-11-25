/* ===== deck engine ===== */
(function () {
  const slides = Array.from(document.querySelectorAll('.slide'));
  const hudNum = document.querySelector('#hud .num');
  const hudBar = document.querySelector('#hud .bar i');
  const notes = document.getElementById('notes');
  const toast = document.getElementById('toast');
  let current = 0;
  let toastTimer = null;

  function showToast(msg) {
    toast.textContent = msg;
    toast.style.display = 'block';
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (toast.style.display = 'none'), 2200);
  }

  function go(i, push) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    if (i === current && slides[i].classList.contains('active')) return;
    slides[current].classList.remove('active');
    deactivateVideo(slides[current]);
    current = i;
    const s = slides[current];
    s.classList.add('active');
    activateVideo(s);
    renderMapIfNeeded(s);
    hudNum.textContent = String(i + 1).padStart(2, '0') + ' / ' + String(slides.length).padStart(2, '0');
    hudBar.style.width = ((i + 1) / slides.length * 100) + '%';
    const n = s.getAttribute('data-note');
    if (n && notes.classList.contains('on')) notes.textContent = n;
    if (push !== false && history.replaceState) {
      history.replaceState(null, '', '#/' + (i + 1));
    }
    document.title = 'AI · slide ' + (i + 1) + '/' + slides.length;
  }

  function next() { go(current + 1); }
  function prev() { go(current - 1); }

  /* ---------- video handling (with optional start/end segment loop) ---------- */
  function activateVideo(slide) {
    slide.querySelectorAll('.yt').forEach(el => {
      const id = el.getAttribute('data-id');
      if (!id || el.querySelector('iframe')) return;
      const th = el.querySelector('.thumb');
      if (th) th.style.display = 'none';
      // no 'start'/'end' params: YouTube ignores them on loop, causing restarts mid-video.
      // Videos always play from 0:00 to the real end, then loop from the beginning.
      const src = 'https://www.youtube.com/embed/' + id +
        '?autoplay=1&loop=1&playlist=' + id + '&rel=0&playsinline=1&modestbranding=1';
      const iframe = document.createElement('iframe');
      iframe.src = src;
      iframe.allow = 'autoplay; encrypted-media; picture-in-picture';
      iframe.allowFullscreen = true;
      el.appendChild(iframe);
    });
  }
  function deactivateVideo(slide) {
    slide.querySelectorAll('.yt').forEach(el => {
      const iframe = el.querySelector('iframe');
      if (iframe) iframe.remove();
      const th = el.querySelector('.thumb');
      if (th) th.style.display = '';
    });
  }
  document.addEventListener('click', e => {
    const th = e.target.closest('.yt .thumb');
    if (th) {
      const slide = th.closest('.slide');
      if (slide && slide.classList.contains('active')) activateVideo(slide);
    }
  });

  /* ---------- agenda boxes → jump to section ---------- */
  document.querySelectorAll('.ag[data-goto]').forEach(ag => {
    ag.addEventListener('click', () => {
      go(parseInt(ag.getAttribute('data-goto'), 10) - 1);
      showToast('Sezione ' + ag.querySelector('.n').textContent + ' → slide ' + ag.getAttribute('data-goto'));
    });
  });

  /* ---------- quiz slide: click reveals names/companies ---------- */
  const quizSlide = document.getElementById('quizslide');
  const peopleGrid = document.getElementById('peopleGrid');
  if (quizSlide && peopleGrid) {
    quizSlide.addEventListener('click', () => {
      peopleGrid.classList.toggle('revealed');
      showToast(peopleGrid.classList.contains('revealed') ? 'Nomi e aziende rivelati ✔' : 'Quiz: solo facce 🙂');
    });
  }

  /* ---------- keyboard / click ---------- */
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); next(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
    else if (e.key === 'Home') go(0);
    else if (e.key === 'End') go(slides.length - 1);
    else if (e.key === 'f') { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); else document.exitFullscreen(); }
    else if (e.key === 'n') {
      notes.classList.toggle('on');
      const n = slides[current].getAttribute('data-note');
      notes.textContent = n || 'Nessuna nota per questa slide.';
    }
  });
  const zp = document.querySelector('.clickzone.prev'); if (zp) zp.addEventListener('click', prev);
  const zn = document.querySelector('.clickzone.next'); if (zn) zn.addEventListener('click', next);

  /* ---------- world map ---------- */
  const W = 1000, H = 500;
  function proj(lon, lat) { return [ (lon + 180) / 360 * W, (90 - lat) / 180 * H ]; }
  function pathFromCoords(coords) {
    let d = '';
    coords.forEach((c, i) => {
      if (!c) return;
      const p = proj(c[0], Math.max(-60, c[1]));
      d += (i === 0 ? 'M' : 'L') + p[0].toFixed(1) + ' ' + p[1].toFixed(1);
    });
    return d;
  }
  function buildLand(svg) {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    (window.WORLD_GEOJSON.features || []).forEach(f => {
      const name = (f.properties && f.properties.name) || '';
      if (name === 'Antarctica') return;
      const geom = f.geometry;
      const polys = geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates;
      polys.forEach(poly => {
        poly.forEach(ring => {
          const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          p.setAttribute('d', pathFromCoords(ring) + 'Z');
          p.setAttribute('class', 'land');
          g.appendChild(p);
        });
      });
    });
    svg.appendChild(g);
  }

  const HUBS = [
    [-77.5, 39.0, 6.0, 'N. Virginia'], [-122.9, 45.5, 1.2, 'Hillsboro'], [-111.9, 33.4, 1.0, 'Phoenix'],
    [-96.8, 32.8, 1.3, 'Dallas'], [-87.6, 41.9, 0.9, 'Chicago'], [-84.4, 33.7, 0.8, 'Atlanta'],
    [-83.0, 40.0, 0.8, 'Columbus'], [-112.0, 40.6, 0.9, 'Salt Lake'], [-121.9, 37.4, 0.9, 'Silicon Valley'],
    [-6.3, 53.3, 1.1, 'Dublino'], [8.7, 50.1, 1.3, 'Francoforte'], [4.9, 52.4, 0.9, 'Amsterdam'],
    [-0.1, 51.5, 1.1, 'Londra'], [2.3, 48.9, 0.6, 'Parigi'], [-3.7, 40.4, 0.5, 'Madrid'],
    [9.2, 45.5, 0.5, 'Milano'], [18.1, 59.3, 0.6, 'Stoccolma'], [21.0, 52.2, 0.4, 'Varsavia'],
    [28.0, -26.2, 0.3, 'Johannesburg'], [55.3, 25.2, 0.5, 'Dubai'], [72.9, 19.1, 0.6, 'Mumbai'],
    [103.8, 1.35, 1.3, 'Singapore'], [106.8, -6.2, 0.4, 'Giacarta'], [101.7, 3.1, 0.3, 'Kuala Lumpur'],
    [139.7, 35.7, 1.3, 'Tokyo'], [127.0, 37.5, 0.7, 'Seoul'], [151.2, -33.9, 0.7, 'Sydney'],
    [-46.6, -23.5, 0.8, 'San Paolo'], [-70.7, -33.4, 0.3, 'Santiago'], [-100.4, 20.6, 0.3, 'Querétaro'],
    [116.4, 39.9, 1.1, 'Pechino'], [121.5, 31.2, 1.0, 'Shanghai'], [106.6, 26.6, 0.8, 'Guizhou'],
    [114.1, 22.3, 0.7, 'Shenzhen'], [121.5, 25.0, 0.5, 'Taipei'],
  ];
  const CABLES = [
    ['MAREA', [[-75.9, 36.9], [-40, 38], [-3.0, 43.4]]],
    ['Dunant', [[-75.9, 36.9], [-38, 44], [-1.9, 46.7]]],
    ['Grace Hopper', [[-72.9, 40.8], [-38, 48], [-4.5, 50.8]]],
    ['EllaLink', [[-8.9, 37.9], [-24, 20], [-38.4, -3.8]]],
    ['Amitié', [[-75.9, 36.9], [-40, 42], [-1.2, 45.6]]],
    ['SEACOM', [[72.8, 19.0], [50, 12], [43.1, 11.6], [39.7, -4.0], [32.6, -25.9], [18.4, -33.9]]],
    ['EASSy', [[36.8, -32.4], [39.7, -4.0], [44.4, -20.3], [51.3, -9.7], [-9.4, 50.4]]],
    ['WACS', [[-12.3, 41.2], [3.4, 6.5], [9.4, -6.9], [-22.9, -23.2], [11.8, -17.0]]],
    ['APG', [[103.8, 1.35], [121.8, 25.3], [139.7, 35.7], [144.7, 13.4], [154.0, -27.5]]],
    ['SAC', [[-75.9, 36.9], [-155.6, 20.0], [151.2, -33.9], [174.8, -41.3]]],
    ['Tata TGN', [[-0.1, 51.5], [-74.0, 40.7], [72.8, 19.0]]],
    ['SAm-1', [[-38.4, -3.8], [-46.6, -23.5], [18.4, -33.9], [28.2, -26.2]]],
  ];
  const CUTS = [
    [42.8, 13.6, 'Mar Rosso · feb 2024'],
    [19.5, 59.8, 'Baltico: 10 cavi tagliati dal 2022'],
    [121.5, 23.5, 'Taiwan: 5 incidenti 2024-25'],
  ];
  // energy mode bubbles: [lon, lat, share%, label]
  const ENERGY = [
    [-100, 45, 45, 'USA 45%'], [105, 35, 25, 'Cina 25%'],
    [15, 50, 15, 'Europa 15%'], [60, -5, 15, 'Resto 15%'],
  ];

  function renderMapIfNeeded(slide) {
    const holder = slide.querySelector('.mapwrap');
    if (!holder || holder.getAttribute('data-done')) return;
    holder.setAttribute('data-done', '1');
    const mode = holder.getAttribute('data-mode') || 'hubs';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    buildLand(svg);

    if (mode === 'cables') {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      CABLES.forEach(([name, pts]) => {
        let d = '';
        const p0 = proj(pts[0][0], pts[0][1]);
        d = 'M' + p0[0].toFixed(1) + ' ' + p0[1].toFixed(1);
        for (let i = 1; i < pts.length - 1; i++) {
          const p = proj(pts[i][0], pts[i][1]);
          const pn = proj(pts[i + 1][0], pts[i + 1][1]);
          const mx = (p[0] + pn[0]) / 2, my = (p[1] + pn[1]) / 2;
          d += ' Q' + p[0].toFixed(1) + ' ' + p[1].toFixed(1) + ' ' + mx.toFixed(1) + ' ' + my.toFixed(1);
        }
        const last = proj(pts[pts.length - 1][0], pts[pts.length - 1][1]);
        d += ' L' + last[0].toFixed(1) + ' ' + last[1].toFixed(1);
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d); path.setAttribute('class', 'cable');
        g.appendChild(path);
      });
      CUTS.forEach(([lon, lat, lbl]) => {
        const p = proj(lon, lat);
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', 7);
        c.setAttribute('class', 'cut pulse');
        g.appendChild(c);
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', p[0] + 12); t.setAttribute('y', p[1] - 8);
        t.setAttribute('class', 'hub-label'); t.setAttribute('fill', '#fda4af');
        t.textContent = lbl;
        g.appendChild(t);
      });
      svg.appendChild(g);
    }

    if (mode === 'energy') {
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      ENERGY.forEach(([lon, lat, share, label]) => {
        const p = proj(lon, lat);
        const r = 14 + Math.sqrt(share) * 9;
        const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        glow.setAttribute('cx', p[0]); glow.setAttribute('cy', p[1]); glow.setAttribute('r', r);
        glow.setAttribute('fill', 'rgba(251,191,36,.14)');
        g.appendChild(glow);
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', r * 0.62);
        c.setAttribute('fill', 'rgba(251,191,36,.55)');
        c.setAttribute('stroke', '#fbbf24'); c.setAttribute('stroke-width', '1');
        g.appendChild(c);
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', p[0]); t.setAttribute('y', p[1] + 4);
        t.setAttribute('text-anchor', 'middle');
        t.setAttribute('class', 'hub-label'); t.setAttribute('fill', '#0b0f1a');
        t.setAttribute('style', 'font-weight:700; font-size:12px; fill:#1a1206;');
        t.textContent = label;
        g.appendChild(t);
      });
      svg.appendChild(g);
    }

    if (mode === 'hubs' || mode === 'cables') {
      const gh = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      HUBS.forEach(([lon, lat, gw, label]) => {
        const p = proj(lon, lat);
        const r = 2.2 + Math.sqrt(gw) * 4.2;
        const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        glow.setAttribute('cx', p[0]); glow.setAttribute('cy', p[1]); glow.setAttribute('r', r);
        glow.setAttribute('class', 'hub-glow pulse');
        gh.appendChild(glow);
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('cx', p[0]); c.setAttribute('cy', p[1]); c.setAttribute('r', r * 0.45);
        c.setAttribute('class', 'hub');
        gh.appendChild(c);
        if (gw >= 1.0 || label === 'N. Virginia') {
          const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
          t.setAttribute('x', p[0] + r * 0.6 + 3); t.setAttribute('y', p[1] - r * 0.5);
          t.setAttribute('class', 'hub-label');
          t.textContent = label + ' · ~' + gw + ' GW';
          gh.appendChild(t);
        }
      });
      svg.appendChild(gh);
    }
    holder.appendChild(svg);
  }

  /* ---------- boot ---------- */
  const m = location.hash.match(/#\/(\d+)/);
  go(m ? parseInt(m[1], 10) - 1 : 0, false);
  window.addEventListener('hashchange', () => {
    const mm = location.hash.match(/#\/(\d+)/);
    if (mm) go(parseInt(mm[1], 10) - 1, false);
  });
  requestAnimationFrame(() => slides.forEach(renderMapIfNeeded));
  showToast('→ frecce per avanzare · F fullscreen · N note relatore');
})();

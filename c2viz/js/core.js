// c2viz/js/core.js: the pixel toolkit (site/assets/scene.js): seeded random numbers, string hashes, value noise, the low-resolution canvas (Px). Knows nothing of the engine.
(function (X) {
  "use strict";
  // ---------------------------------------------------------------------------------------------------- toolkit (scene.js)
  function rng(s) { return function () { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  function hstr(s) { let h = 2166136261; for (const c of String(s)) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; }
  function noise(seed) {
    const H = (x, y) => { let h = (seed ^ Math.imul(x, 374761393) ^ Math.imul(y, 668265263)) | 0; h = Math.imul(h ^ h >>> 13, 1274126177); return ((h ^ h >>> 16) >>> 0) / 4294967296; };
    const sm = (t) => t * t * (3 - 2 * t);
    const v = (x, y) => { const ix = Math.floor(x), iy = Math.floor(y), fx = sm(x - ix), fy = sm(y - iy); const a = H(ix, iy), b = H(ix + 1, iy), c = H(ix, iy + 1), d = H(ix + 1, iy + 1); return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy; };
    return (x, y, o = 4) => { let s = 0, a = 1, f = 1, n = 0; for (let i = 0; i < o; i++) { s += v(x * f + i * 17.3, y * f + i * 9.1) * a; n += a; a *= 0.5; f *= 2; } return s / n; };
  }
  const C = (h) => parseInt(h.slice(1), 16);
  function Px(cv, W, H, bg) {
    cv.width = W; cv.height = H;
    const g = cv.getContext("2d"), img = g.createImageData(W, H), d = img.data, buf = new Uint32Array(W * H).fill(bg ? C(bg) : 0);
    const put = (x, y, c) => { x |= 0; y |= 0; if (x >= 0 && y >= 0 && x < W && y < H) buf[y * W + x] = typeof c === "string" ? C(c) : c; };
    const get = (x, y) => buf[(y | 0) * W + (x | 0)];
    const shade = (x, y, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const c = buf[y * W + x];
      const f = (v) => Math.max(0, Math.min(255, Math.round(t >= 0 ? v * (1 - t) : v + (255 - v) * -t)));
      buf[y * W + x] = (f(c >> 16 & 255) << 16) | (f(c >> 8 & 255) << 8) | f(c & 255); };
    const mix = (x, y, col, t) => { x |= 0; y |= 0; if (x < 0 || y < 0 || x >= W || y >= H) return; const a = buf[y * W + x], b = typeof col === "string" ? C(col) : col;
      const m = (s) => Math.round((a >> s & 255) * (1 - t) + (b >> s & 255) * t); buf[y * W + x] = (m(16) << 16) | (m(8) << 8) | m(0); };
    const flush = () => { for (let i = 0; i < W * H; i++) { const c = buf[i]; d[i * 4] = c >> 16 & 255; d[i * 4 + 1] = c >> 8 & 255; d[i * 4 + 2] = c & 255; d[i * 4 + 3] = 255; } g.putImageData(img, 0, 0); };
    return { put, get, dark: (x, y, t) => shade(x, y, t), light: (x, y, t) => shade(x, y, -t), mix, flush, W, H, save: () => buf.slice(), restore: (b) => buf.set(b) };
  }
  Object.assign(X, { rng, hstr, noise, C, Px });
})(C2X);

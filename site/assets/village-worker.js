// Draws run villages off the main thread (village() takes ~200-300 ms each). Receives {id, seed, cfg}, answers with an
// ImageBitmap plus the hotspot layout village() returns.
import { village } from "./scene.js";

self.onmessage = (e) => {
  const { id, seed, cfg } = e.data;
  try {
    const cv = new OffscreenCanvas(cfg.width || 240, cfg.height || 150);
    const out = village(cv, seed, { ...cfg, roles: new Set(cfg.roles) });
    const bmp = cv.transferToImageBitmap();
    self.postMessage({ id, out, bmp, w: cv.width, h: cv.height }, [bmp]);
  } catch (err) {
    self.postMessage({ id, error: String(err && err.stack || err) });
  }
};

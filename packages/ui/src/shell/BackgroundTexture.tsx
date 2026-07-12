"use client";

import { useEffect, useRef } from "react";

const NOISE_SCALE = 4;
const FIBER_PER_MPX = 150;
const BLOT_PER_MPX = 18;

// "Warm archive" paper texture, faithful to the reference mockup: a very faint
// bright speckle (paper grain) over the page's own deep-blue base, plus thin
// dark ink fibers and soft dark vignette blots. Everything is dark-on-dark and
// low-alpha — it must whisper, never tint the page brown.
function paintTexture(canvas: HTMLCanvasElement, ratio: number) {
  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  if (!ctx || width <= 0 || height <= 0) return;

  ctx.clearRect(0, 0, width, height);

  // 1. Sparse bright grain — generated at 1/4 resolution and upscaled so we
  //    never touch full-resolution ImageData on the main thread.
  const noiseW = Math.max(1, Math.ceil(width / NOISE_SCALE));
  const noiseH = Math.max(1, Math.ceil(height / NOISE_SCALE));
  const noise = document.createElement("canvas");
  noise.width = noiseW;
  noise.height = noiseH;
  const nctx = noise.getContext("2d");
  if (nctx) {
    const image = nctx.createImageData(noiseW, noiseH);
    const data = image.data;
    for (let i = 0; i < data.length; i += 4) {
      const v = Math.random() * 255;
      const bright = v > 218 ? v : 0;
      data[i] = data[i + 1] = data[i + 2] = bright;
      data[i + 3] = bright ? Math.floor(((bright - 218) / 37) * 10) : 0;
    }
    nctx.putImageData(image, 0, 0);
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(noise, 0, 0, noiseW, noiseH, 0, 0, width, height);
    ctx.imageSmoothingEnabled = true;
  }

  const megapixels = (width * height) / (ratio * ratio) / 1_000_000;

  // 2. Thin dark ink fibers.
  const fiberCount = Math.round(FIBER_PER_MPX * Math.max(0.3, megapixels));
  for (let i = 0; i < fiberCount; i += 1) {
    const px = Math.random() * width;
    const py = Math.random() * height;
    const len = (Math.random() * 220 + 20) * ratio;
    const dx = (Math.random() - 0.5) * 14 * ratio;
    ctx.beginPath();
    ctx.moveTo(px, py);
    ctx.bezierCurveTo(
      px + (Math.random() - 0.5) * 6 * ratio,
      py + len * 0.32,
      px + dx * 0.5,
      py + len * 0.7,
      px + dx,
      py + len,
    );
    ctx.lineWidth = (Math.random() * 0.45 + 0.06) * ratio;
    ctx.strokeStyle = `rgba(6, 5, 9, ${Math.random() * 0.13 + 0.02})`;
    ctx.stroke();
  }

  // 3. Soft dark vignette blots.
  const blotCount = Math.round(BLOT_PER_MPX * Math.max(0.3, megapixels));
  for (let i = 0; i < blotCount; i += 1) {
    const px = Math.random() * width;
    const py = Math.random() * height;
    const r = (Math.random() * 90 + 12) * ratio;
    const gradient = ctx.createRadialGradient(px, py, 0, px, py, r);
    gradient.addColorStop(0, `rgba(4, 4, 9, ${Math.random() * 0.09 + 0.02})`);
    gradient.addColorStop(1, "rgba(4, 4, 9, 0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.ellipse(
      px,
      py,
      r,
      r * (0.3 + Math.random() * 0.7),
      Math.random() * Math.PI,
      0,
      Math.PI * 2,
    );
    ctx.fill();
  }
}

export function BackgroundTexture() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const render = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, Math.round(rect.width * ratio));
      canvas.height = Math.max(1, Math.round(rect.height * ratio));
      paintTexture(canvas, ratio);
    };
    render();

    let lastWidth = canvas.getBoundingClientRect().width;
    let resizeTimer: ReturnType<typeof setTimeout> | undefined;
    const handleResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        const currentWidth = canvas.getBoundingClientRect().width;
        if (Math.abs(currentWidth - lastWidth) < 1) return;
        lastWidth = currentWidth;
        render();
      }, 250);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      clearTimeout(resizeTimer);
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className="pointer-events-none fixed inset-0 z-0 h-full w-full"
    />
  );
}

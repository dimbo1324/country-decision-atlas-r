import { useEffect, useRef } from "react";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";

const TEXTURE_SCALE = 0.22;
const MAX_TEXTURE_WIDTH = 420;
const MAX_TEXTURE_HEIGHT = 300;
const FIBER_COUNT = 14;
const BLOTCH_COUNT = 6;

function paintTexture(
  canvas: HTMLCanvasElement,
  width: number,
  height: number,
) {
  const ctx = canvas.getContext("2d");
  if (!ctx || width <= 0 || height <= 0) return;

  const texW = Math.max(
    1,
    Math.min(MAX_TEXTURE_WIDTH, Math.round(width * TEXTURE_SCALE)),
  );
  const texH = Math.max(
    1,
    Math.min(MAX_TEXTURE_HEIGHT, Math.round(height * TEXTURE_SCALE)),
  );

  const offscreen = document.createElement("canvas");
  offscreen.width = texW;
  offscreen.height = texH;
  const octx = offscreen.getContext("2d");
  if (!octx) return;

  const fiber = readCssVar("--color-c4") || "#494436";
  const blotch = readCssVar("--color-terra2") || "#8a4e34";

  const imageData = octx.createImageData(texW, texH);
  for (let i = 0; i < imageData.data.length; i += 4) {
    const shade = 205 + Math.floor(Math.random() * 50);
    imageData.data[i] = shade;
    imageData.data[i + 1] = shade;
    imageData.data[i + 2] = shade;
    imageData.data[i + 3] = Math.random() < 0.5 ? 5 : 9;
  }
  octx.putImageData(imageData, 0, 0);

  octx.strokeStyle = withAlpha(fiber, 0.16);
  octx.lineWidth = 1;
  for (let i = 0; i < FIBER_COUNT; i += 1) {
    octx.beginPath();
    octx.moveTo(Math.random() * texW, Math.random() * texH);
    octx.bezierCurveTo(
      Math.random() * texW,
      Math.random() * texH,
      Math.random() * texW,
      Math.random() * texH,
      Math.random() * texW,
      Math.random() * texH,
    );
    octx.stroke();
  }

  for (let i = 0; i < BLOTCH_COUNT; i += 1) {
    const x = Math.random() * texW;
    const y = Math.random() * texH;
    const radius = texW * (0.14 + Math.random() * 0.24);
    const gradient = octx.createRadialGradient(x, y, 0, x, y, radius);
    gradient.addColorStop(0, withAlpha(blotch, 0.2));
    gradient.addColorStop(1, withAlpha(blotch, 0));
    octx.fillStyle = gradient;
    octx.beginPath();
    octx.arc(x, y, radius, 0, Math.PI * 2);
    octx.fill();
  }

  ctx.clearRect(0, 0, width, height);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(offscreen, 0, 0, texW, texH, 0, 0, width, height);
}

export function BackgroundTexture() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const render = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, rect.width * ratio);
      canvas.height = Math.max(1, rect.height * ratio);
      paintTexture(canvas, canvas.width, canvas.height);
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

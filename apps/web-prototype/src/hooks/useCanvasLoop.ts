import { type RefObject, useEffect, useRef } from "react";

export function useCanvasLoop(
  ref: RefObject<HTMLCanvasElement | null>,
  draw: (ctx: CanvasRenderingContext2D, width: number, height: number) => void,
  active: boolean,
) {
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas || !active) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const ratio = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, rect.width * ratio);
      canvas.height = Math.max(1, rect.height * ratio);
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    };
    resize();

    let widthAtLastResize = canvas.getBoundingClientRect().width;
    let resizeTimer: ReturnType<typeof setTimeout> | undefined;
    const handleResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        const currentWidth = canvas.getBoundingClientRect().width;
        if (Math.abs(currentWidth - widthAtLastResize) < 1) return;
        widthAtLastResize = currentWidth;
        resize();
      }, 200);
    };
    window.addEventListener("resize", handleResize);

    const tick = () => {
      const rect = canvas.getBoundingClientRect();
      draw(ctx, rect.width, rect.height);
      frameRef.current = requestAnimationFrame(tick);
    };
    frameRef.current = requestAnimationFrame(tick);

    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
      clearTimeout(resizeTimer);
      window.removeEventListener("resize", handleResize);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, ref]);
}

export function lerp(current: number, target: number, factor = 0.055): number {
  return current + (target - current) * factor;
}

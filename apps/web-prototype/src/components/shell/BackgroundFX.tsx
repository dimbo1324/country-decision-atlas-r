import { useRef } from "react";
import { useCanvasLoop } from "@/hooks/useCanvasLoop";
import { readCssVar, withAlpha } from "@/components/charts/chartColors";
import { useReducedMotion } from "@/hooks/useReducedMotion";

interface Particle {
  x: number;
  y: number;
  radius: number;
  speed: number;
  phase: number;
}

const MAX_PARTICLES = 46;

export function BackgroundFX() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[] | null>(null);
  const reducedMotion = useReducedMotion();

  useCanvasLoop(
    canvasRef,
    (ctx, width, height) => {
      if (!particlesRef.current || particlesRef.current.length === 0) {
        const count = Math.min(
          MAX_PARTICLES,
          Math.round((width * height) / 26000),
        );
        particlesRef.current = Array.from({ length: count }, () => ({
          x: Math.random() * width,
          y: Math.random() * height,
          radius: 0.6 + Math.random() * 1.2,
          speed: 0.08 + Math.random() * 0.16,
          phase: Math.random() * Math.PI * 2,
        }));
      }

      const gold = readCssVar("--color-gold") || "#d8aa4e";
      ctx.clearRect(0, 0, width, height);

      particlesRef.current.forEach((particle) => {
        particle.y -= particle.speed;
        particle.phase += 0.01;
        if (particle.y < -10) {
          particle.y = height + 10;
          particle.x = Math.random() * width;
        }
        const alpha = 0.15 + Math.sin(particle.phase) * 0.1;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = withAlpha(gold, Math.max(0.04, alpha));
        ctx.fill();
      });
    },
    !reducedMotion,
  );

  return (
    <canvas
      ref={canvasRef}
      aria-hidden
      className="pointer-events-none fixed inset-0 z-0 h-full w-full"
    />
  );
}

import {
  type MouseEvent,
  type ReactNode,
  useCallback,
  useRef,
  useState,
} from "react";
import { cn } from "@/lib/cn";
import { ACCENTS, type Accent } from "@/lib/accents";

interface CardProps {
  accent?: Accent;
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  interactive?: boolean;
}

export function Card({
  accent = "gold",
  children,
  onClick,
  className,
  interactive = true,
}: CardProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ x: 0, y: 0 });
  const [glow, setGlow] = useState({ x: 50, y: 50, active: false });
  const accentClasses = ACCENTS[accent];

  const handleMouseMove = useCallback((event: MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;
    setTilt({ x: (py - 0.5) * -8, y: (px - 0.5) * 8 });
    setGlow({ x: px * 100, y: py * 100, active: true });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 });
    setGlow((prev) => ({ ...prev, active: false }));
  }, []);

  return (
    <div
      ref={ref}
      onMouseMove={interactive ? handleMouseMove : undefined}
      onMouseLeave={interactive ? handleMouseLeave : undefined}
      onClick={onClick}
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{
        transform: interactive
          ? `perspective(900px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) translateY(${tilt.x !== 0 || tilt.y !== 0 ? -3 : 0}px)`
          : undefined,
        transition: "transform 0.4s var(--ease-arrive), border-color 0.3s",
      }}
      className={cn(
        "bg-bg2 border-warm relative overflow-hidden border p-6",
        onClick && "cursor-pointer",
        interactive && "hover:border-warm-hi",
        className,
      )}
    >
      <span
        className={cn(
          "absolute inset-x-0 top-0 h-[2px] origin-left scale-x-0 transition-transform duration-500",
          accentClasses.bg,
        )}
        style={{
          transform: glow.active ? "scaleX(1)" : "scaleX(0)",
        }}
      />
      {interactive && glow.active && (
        <div
          className="pointer-events-none absolute inset-0 opacity-60"
          style={{
            background: `radial-gradient(220px circle at ${glow.x}% ${glow.y}%, rgb(216 170 78 / 0.05), transparent 70%)`,
          }}
        />
      )}
      <div className="relative">{children}</div>
    </div>
  );
}

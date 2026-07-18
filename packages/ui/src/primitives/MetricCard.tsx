"use client";

import type { LucideIcon } from "lucide-react";
import { Card } from "./Card";
import type { Accent } from "../lib/accents";

interface MetricCardProps {
  icon: LucideIcon;
  name: string;
  tag: string;
  description: string;
  value: string;
  unit: string;
  accent: Accent;
}

/** The mockup's "mcard": framed icon, name, mono tag, body, hero value. */
export function MetricCard({
  icon: Icon,
  name,
  tag,
  description,
  value,
  unit,
  accent,
}: MetricCardProps) {
  return (
    <Card
      accent={accent}
      className="flex h-full flex-col gap-4"
    >
      <span
        className="flex h-10 w-10 items-center justify-center border"
        style={{
          borderColor: `var(--color-${accent}2)`,
          color: `var(--color-${accent})`,
        }}
      >
        <Icon
          width={18}
          height={18}
          strokeWidth={1.5}
        />
      </span>
      <div className="flex flex-col gap-1">
        <h3 className="font-display text-lg leading-snug font-semibold">
          {name}
        </h3>
        <span className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
          {tag}
        </span>
      </div>
      <p className="text-c3 flex-1 text-sm leading-relaxed">{description}</p>
      <div className="flex items-baseline gap-2">
        <b
          className="font-display text-3xl leading-none font-bold"
          style={{ color: `var(--color-${accent}3)` }}
        >
          {value}
        </b>
        <span className="font-mono text-c3 text-[9px] tracking-[0.15em] uppercase">
          {unit}
        </span>
      </div>
    </Card>
  );
}

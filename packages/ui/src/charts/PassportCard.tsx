"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowRight, Download, Link2, ShieldCheck } from "lucide-react";
import { cn } from "../lib/cn";
import { Toggle } from "../primitives/Toggle";
import type { PassportData } from "./types";

interface PassportCardProps {
  passport: PassportData;
  active: boolean;
}

/** A number that glides between targets with the house ease-out cubic —
 * unlike Counter it re-animates every time the target changes, which is
 * exactly what the passport's live recalculation needs. The ref mirrors
 * what's actually on screen, so a restarted effect (target change mid-glide,
 * StrictMode's double-run) resumes from the visible value; the cleanup only
 * cancels the frame and never fakes a completed animation. */
function GlidingNumber({ value }: { value: number }) {
  const [display, setDisplay] = useState(value);
  const displayRef = useRef(value);

  useEffect(() => {
    const from = displayRef.current;
    if (from === value) return;
    const start = performance.now();
    const durationMs = 700;
    let frame: number;
    const step = (now: number) => {
      const progress = Math.min(1, (now - start) / durationMs);
      const eased = 1 - (1 - progress) ** 3;
      const next = Math.round(from + (value - from) * eased);
      displayRef.current = next;
      setDisplay(next);
      if (progress < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  return <>{display}</>;
}

/** The mockup's Decision Passport: a tangible, stamped document artifact.
 * The two toggles feed the CBLC score live — flipping them recomputes the
 * number with a glide, so the document feels computed, not printed. This
 * animation is driven by a genuine user-triggered recalculation, not
 * decorative breathing, so it has no `live`/`static` mode of its own. */
export function PassportCard({ passport, active }: PassportCardProps) {
  const [withTaxTreaty, setWithTaxTreaty] = useState(true);
  const [nomadMode, setNomadMode] = useState(false);

  const score =
    passport.baseScore +
    (withTaxTreaty ? passport.taxTreatyBonus : 0) +
    (nomadMode ? passport.nomadBonus : 0);

  const scoreTone =
    score >= 72 ? "text-sage3" : score >= 55 ? "text-gold3" : "text-terra3";

  return (
    <div className="border-warm bg-bg2 relative flex flex-col border">
      {/* Perforated top edge: the document reads as torn off a ledger. */}
      <div
        aria-hidden
        className="border-warm h-[3px] w-full border-b"
        style={{
          backgroundImage:
            "repeating-linear-gradient(90deg, transparent 0 7px, rgb(239 230 212 / 0.14) 7px 10px)",
        }}
      />

      <div className="flex items-start justify-between gap-4 p-6 pb-4">
        <div className="flex min-w-0 flex-col gap-2.5">
          <span className="font-mono text-c4 text-[9px] tracking-[0.25em] uppercase">
            Паспорт решения · {passport.reference}
          </span>
          <span className="font-display text-c1 flex items-center gap-3 text-2xl font-semibold">
            <span className="truncate">{passport.fromName}</span>
            <ArrowRight
              width={18}
              height={18}
              strokeWidth={1.5}
              className="text-gold shrink-0"
            />
            <span className="truncate">{passport.toName}</span>
          </span>
          <span className="font-mono text-c4 text-[8px] tracking-[0.2em] uppercase">
            {passport.fromFlag} → {passport.toFlag} · маршрут проверен
          </span>
        </div>
        <span
          className="border-gold2/70 text-gold flex h-14 w-14 shrink-0 rotate-6 items-center justify-center rounded-full border-2 border-dashed"
          aria-hidden
        >
          <ShieldCheck
            width={22}
            height={22}
            strokeWidth={1.5}
          />
        </span>
      </div>

      <div className="border-warm grid grid-cols-2 border-y sm:grid-cols-4">
        {[
          {
            label: "Скор CBLC",
            value: (
              <span className={cn("transition-colors duration-500", scoreTone)}>
                <GlidingNumber value={active ? score : 0} />
              </span>
            ),
          },
          { label: "Виза / въезд", value: passport.visaLabel },
          {
            label: "Налог. соглашение",
            value: withTaxTreaty ? (
              <span className="text-sage3">Учтено</span>
            ) : (
              <span className="text-c3">Исключено</span>
            ),
          },
          { label: "Сдвиг времени", value: passport.timezoneShift },
        ].map((cell, index) => (
          <div
            key={cell.label}
            className={cn(
              "border-warm flex flex-col gap-1.5 p-4",
              index < 3 && "border-r max-sm:[&:nth-child(2)]:border-r-0",
            )}
          >
            <span className="font-mono text-c4 text-[8px] tracking-[0.18em] uppercase">
              {cell.label}
            </span>
            <span className="font-display text-c1 text-xl leading-none font-bold">
              {cell.value}
            </span>
          </div>
        ))}
      </div>

      <div className="border-warm flex flex-col gap-3 border-b p-5">
        <Toggle
          checked={withTaxTreaty}
          onChange={setWithTaxTreaty}
          label="Учитывать налоговое соглашение"
          hint={`+${passport.taxTreatyBonus} к скору совместимости`}
          accent="sage"
        />
        <Toggle
          checked={nomadMode}
          onChange={setNomadMode}
          label="Режим цифрового кочевника"
          hint={`+${passport.nomadBonus} · веса сценария смещаются к удалённой работе`}
          accent="blue"
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-4 p-5">
        <div className="flex flex-wrap gap-2">
          {[
            "Source-backed",
            `Достоверность ${passport.confidence.toFixed(2)}`,
            `Проверено ${passport.verifiedOn}`,
          ].map((tag) => (
            <span
              key={tag}
              className="border-warm text-c3 font-mono px-2 py-1 text-[8px] tracking-[0.15em] uppercase"
            >
              {tag}
            </span>
          ))}
        </div>
        <div className="flex gap-2.5">
          {[
            { icon: Download, label: "Экспорт PDF" },
            { icon: Link2, label: "Ссылка" },
          ].map(({ icon: ActionIcon, label }) => (
            <button
              key={label}
              type="button"
              className="group border-warm text-c2 hover:border-gold2 hover:text-gold3 font-mono relative inline-flex items-center gap-2 overflow-hidden border px-3.5 py-2 text-[9px] tracking-[0.2em] uppercase transition-colors duration-300"
            >
              <ActionIcon
                width={12}
                height={12}
                strokeWidth={1.5}
                className="transition-transform duration-300 group-hover:scale-115"
              />
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

import type { Accent } from "./accents";
import type { BadgeVariant } from "../primitives/Badge";

export type ScoreLabel =
  | "weak"
  | "limited"
  | "moderate"
  | "strong"
  | "excellent"
  | "missing";

interface ScoreLabelStyle {
  accent: Accent;
  badgeVariant: BadgeVariant;
}

const SCORE_LABEL_STYLE: Record<ScoreLabel, ScoreLabelStyle> = {
  weak: { accent: "terra", badgeVariant: "critical" },
  limited: { accent: "terra", badgeVariant: "negative" },
  moderate: { accent: "gold", badgeVariant: "warning" },
  strong: { accent: "sage", badgeVariant: "trust" },
  excellent: { accent: "sage", badgeVariant: "positive" },
  missing: { accent: "gold", badgeVariant: "default" },
};

/** Single source of truth for the weak…excellent 5-band score colour
 * semantics — used by the country dossier's scenario scores and the
 * comparison matrix so both surfaces agree on what "strong" looks like. */
export function scoreLabelStyle(
  label: string | null | undefined,
): ScoreLabelStyle {
  return (
    SCORE_LABEL_STYLE[(label as ScoreLabel) ?? "missing"] ??
    SCORE_LABEL_STYLE.missing
  );
}

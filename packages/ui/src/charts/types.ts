import type { Accent } from "../lib/accents";
import type { Confidence } from "../lib/confidence";

export type { Confidence } from "../lib/confidence";

/** Whether a chart keeps subtly breathing around its real value forever
 * ("live", for showcase/overview screens) or settles once and holds the
 * exact data ("static", for analytical screens where the reader trusts the
 * number on screen). The displayed *label* value never changes between
 * modes — only the decorative motion does. */
export type ChartMode = "live" | "static";

/** Shared shape for chart data transparency (design-system §6): every
 * displayed metric carries when it was verified and how confident the
 * platform is in it, so `ChartFrame` can render both consistently. */
export interface ChartDatum {
  label: string;
  value: number;
  min?: number;
  max?: number;
  accent?: Accent;
  verifiedAt?: string;
  confidence?: Confidence;
}

export function accentCssVar(
  accent: Accent,
  tone: "" | "2" | "3" = "",
): string {
  return `--color-${accent}${tone}`;
}

export interface DonutSegment {
  label: string;
  value: number;
  accent: Accent;
}

export interface HeatmapData {
  rows: string[];
  columns: string[];
  values: number[][];
}

export interface RankFlowSeries {
  name: string;
  accent: Accent;
  ranks: number[];
}

export interface DriftBoardRow {
  slug: string;
  name: string;
  flag: string;
  timeline: number[];
  driftValue: number;
  statusLabel: string;
  status: "pos" | "mild" | "stable" | "neg";
}

export interface PassportData {
  reference: string;
  fromName: string;
  fromFlag: string;
  toName: string;
  toFlag: string;
  baseScore: number;
  taxTreatyBonus: number;
  nomadBonus: number;
  visaLabel: string;
  timezoneShift: string;
  confidence: number;
  verifiedOn: string;
}

/** A point on the legal-signals timeline: one event, one country, one
 * impact direction. */
export interface LegalSignalEvent {
  id: string;
  date: string;
  country: string;
  title: string;
  impact: "up" | "down" | "info";
  impactLabel: string;
}

/** One criterion's contribution to a decision score. */
export interface CriteriaWeight {
  label: string;
  contribution: number;
  accent?: Accent;
}

import { ArrowLeft, ArrowRight, ExternalLink } from "lucide-react";

/** Lucide replacements for the Unicode link-affordance glyphs
 * (→ ↗ ←). Decorative: the link text carries the meaning, so the
 * icons stay hidden from assistive technology. */

const iconProps = {
  "width": 12,
  "height": 12,
  "strokeWidth": 1.5,
  "aria-hidden": true,
  "className": "inline-block shrink-0 align-[-1px]",
} as const;

export function ArrowNext() {
  return <ArrowRight {...iconProps} />;
}

export function ArrowBack() {
  return <ArrowLeft {...iconProps} />;
}

export function ArrowExternal() {
  return <ExternalLink {...iconProps} />;
}

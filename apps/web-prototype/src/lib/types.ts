import type { ReactNode } from "react";
import type { Accent } from "@/lib/accents";

export interface SlideDef {
  id: string;
  navLabel: string;
  accent: Accent;
  content: ReactNode;
}

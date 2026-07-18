import {
  Crimson_Text,
  IM_Fell_English,
  Playfair_Display,
} from "next/font/google";

// Cyrillic coverage matters here (the UI is Russian-first) but not every
// family in the design system ships a cyrillic subset on Google Fonts —
// Crimson Text and IM Fell English are latin-only upstream, so Cyrillic text
// set in them silently falls through to the Georgia/serif fallback in
// theme.css's font stack. This is an accepted, intentional gap in those
// upstream families, not a bug introduced here.
export const playfairDisplay = Playfair_Display({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-playfair",
  display: "swap",
});

export const crimsonText = Crimson_Text({
  subsets: ["latin"],
  weight: ["400", "600"],
  style: ["normal", "italic"],
  variable: "--font-crimson",
  display: "swap",
});

export const imFellEnglish = IM_Fell_English({
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
  variable: "--font-imfell",
  display: "swap",
});

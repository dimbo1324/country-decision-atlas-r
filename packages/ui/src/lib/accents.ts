export type Accent = "gold" | "blue" | "terra" | "sage" | "plum";

interface AccentClasses {
  border: string;
  borderHover: string;
  text: string;
  textBright: string;
  bg: string;
  dot: string;
}

export const ACCENTS: Record<Accent, AccentClasses> = {
  gold: {
    border: "border-gold2/60",
    borderHover: "hover:border-gold",
    text: "text-gold",
    textBright: "text-gold3",
    bg: "bg-gold",
    dot: "bg-gold",
  },
  blue: {
    border: "border-blue2/60",
    borderHover: "hover:border-blue",
    text: "text-blue",
    textBright: "text-blue3",
    bg: "bg-blue",
    dot: "bg-blue",
  },
  terra: {
    border: "border-terra2/60",
    borderHover: "hover:border-terra",
    text: "text-terra",
    textBright: "text-terra3",
    bg: "bg-terra",
    dot: "bg-terra",
  },
  sage: {
    border: "border-sage2/60",
    borderHover: "hover:border-sage",
    text: "text-sage",
    textBright: "text-sage3",
    bg: "bg-sage",
    dot: "bg-sage",
  },
  plum: {
    border: "border-plum2/60",
    borderHover: "hover:border-plum",
    text: "text-plum",
    textBright: "text-plum3",
    bg: "bg-plum",
    dot: "bg-plum",
  },
};

const REGIONAL_INDICATOR_OFFSET = 0x1f1a5;

/** ISO 3166-1 alpha-2 code -> Unicode flag emoji (each letter maps to a
 * regional indicator symbol; browsers/OSes render the pair as one flag).
 * No image assets, no library — this is the whole implementation. */
export function flagEmoji(iso2: string): string {
  const code = iso2.trim().toUpperCase();
  if (!/^[A-Z]{2}$/.test(code)) return "";
  return String.fromCodePoint(
    ...[...code].map(
      (letter) => letter.codePointAt(0)! + REGIONAL_INDICATOR_OFFSET,
    ),
  );
}

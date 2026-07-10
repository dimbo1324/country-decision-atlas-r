Fonts in this directory are derived from the Noto Sans family (Google Fonts,
`google/fonts` repository, `ofl/` directory), licensed under the SIL Open
Font License 1.1 (`OFL.txt`, same text applies to every font here).

Each `*-Regular.ttf` is a static `wght=400`/`wdth=100` instance produced
from the upstream variable font with `fonttools varLib.instancer`, dropping
unused variation tables.

`NotoSansSC-Regular-Subset.ttf`, `NotoSansJP-Regular-Subset.ttf`, and
`NotoSansKR-Regular-Subset.ttf` are further subsetted with
`fonttools subset` to only the Unicode codepoints actually used by
`docs/synthetic_data/input_data/locale_corpus.json`'s `zh-Hans-CN`/`ja-JP`/
`ko-KR` entries (plus common ASCII/punctuation) — the unmodified upstream
CJK fonts are 6-18 MB each, far above this repository's 1 MB
per-file limit; subsetting keeps every glyph actually needed while staying
well under it. Re-run the subsetting step and widen the codepoint set if
the CJK corpus text changes.

No font in this directory was modified in a way that violates OFL
reserved-name restrictions: file names were changed (as OFL requires when
a font is modified), and the license text is kept alongside every file.

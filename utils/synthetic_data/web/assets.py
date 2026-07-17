from __future__ import annotations

import base64
import html


# Inlined into every page's <style> block, mirroring core/dashboard.py's
# approach -- no separate CSS file, so server.py never needs a static-file
# mount for it.
PAGE_STYLE = """
body { font-family: system-ui, sans-serif; margin: 2rem auto; max-width: 46rem;
  color: #1a1a1a; line-height: 1.5; }
header { border-bottom: 2px solid #ddd; padding-bottom: 0.75rem; margin-bottom: 1.5rem; }
header h1 { margin: 0 0 0.25rem; }
.notice { background: #fff3cd; border: 1px solid #ffe08a; padding: 0.6rem 0.9rem;
  border-radius: 6px; font-weight: 600; font-size: 0.9rem; margin: 0.75rem 0; }
nav.breadcrumbs { font-size: 0.85rem; color: #555; margin-bottom: 1rem; }
nav.breadcrumbs a { color: #1a5fb4; }
ul.links { list-style: none; padding: 0; }
ul.links li { margin: 0.35rem 0; }
a { color: #1a5fb4; }
a.download::before { content: "\\2913  "; }
.comment { border-left: 3px solid #ddd; padding: 0.35rem 0.75rem; margin: 0.5rem 0;
  font-size: 0.92rem; color: #333; }
.comment .meta { color: #777; font-size: 0.8rem; }
footer { margin-top: 3rem; color: #777; font-size: 0.8rem; border-top: 1px solid #eee;
  padding-top: 0.75rem; }
img.placeholder { max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }
"""

_FAVICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="6" fill="#1a5fb4"/>'
    '<text x="16" y="22" font-size="18" text-anchor="middle" fill="#fff" '
    'font-family="sans-serif">S</text></svg>'
)
FAVICON_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(
    _FAVICON_SVG.encode("utf-8")
).decode("ascii")


def placeholder_image_svg(
    *, label: str, width: int = 320, height: int = 180
) -> str:
    """A self-contained inline placeholder image (no binary asset file, no
    network fetch) for pages that want to show "a photo" without any real
    image content -- just a labeled rectangle."""
    safe_label = html.escape(label)
    return (
        f'<svg class="placeholder" xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{safe_label}">'
        f'<rect width="{width}" height="{height}" fill="#e8e8f0"/>'
        f'<text x="{width // 2}" y="{height // 2}" font-size="14" '
        f'text-anchor="middle" dominant-baseline="middle" fill="#555" '
        f'font-family="sans-serif">{safe_label}</text></svg>'
    )

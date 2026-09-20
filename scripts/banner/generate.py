#!/usr/bin/env python3
"""
Generate animated SVG GitHub profile banners for Farah Ben Chikha.
High-density dithered dot-matrix portrait with crisp subject extraction & fast particle animation.

Run from repository root:
    python scripts/banner/generate.py
"""

from __future__ import annotations
import html
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "farah-photo.jpeg"

W, H = 1180, 610
LOOP_SECONDS = 8.0  # Fast, snappy 8-second loop

THEMES = {
    "dark": {
        "bg": "#0A101F",
        "panel": "#0D1628",
        "panel2": "#101B30",
        "line": "#25344C",
        "muted": "#8291A8",
        "text": "#DDE7F5",
        "portrait": "#38BDF8",        # Bright cyber cyan
        "portrait_secondary": "#818CF8",  # Indigo accent
        "chrome": "#22D3EE",
        "accent": "#10B981",
        "shadow": "#02050B",
    },
    "light": {
        "bg": "#F6F8FA",
        "panel": "#FFFFFF",
        "panel2": "#EDF3F7",
        "line": "#CBD7E1",
        "muted": "#64748B",
        "text": "#172033",
        "portrait": "#0284C7",
        "portrait_secondary": "#6366F1",
        "chrome": "#0891B2",
        "accent": "#059669",
        "shadow": "#AAB7C4",
    },
}

ROWS = [
    ("Subject", "FARAH BEN CHIKHA"),
    ("Role", "Cloud & DevOps Engineer"),
    ("Specialties", "Kubernetes · DevSecOps · GitOps · AIOps"),
    ("Education", "ESPRIT 🎓 · Univ of Tokyo (GCI) 🇯🇵"),
    ("Status", "Seeking 6-Month PFE Internship (Jan 2027)"),
    ("Locations", "France · Europe · Remote / Hybrid"),
    ("Cloud.Infra", "Azure · OpenStack · VMware · Kubernetes HA"),
    ("IaC.DevOps", "Terraform · Ansible · Argo CD · Docker"),
    ("Sec.Obs", "HashiCorp Vault · ELK · Prometheus · Grafana"),
    ("AIOps.Tools", "K8sGPT · KubeWatch · Gemini AI · MCP"),
    ("Grid.LinkedIn", "linkedin.com/in/farahbenchikha"),
    ("Grid.GitHub", "github.com/farahbenchikha"),
]


def floyd_steinberg(gray: np.ndarray) -> np.ndarray:
    """Serpentine 1-bit Floyd-Steinberg diffusion dithering."""
    work = gray.astype(np.float32) / 255.0
    out = np.zeros_like(work, dtype=bool)
    height, width = work.shape
    for y in range(height):
        left_to_right = y % 2 == 0
        xs = range(width) if left_to_right else range(width - 1, -1, -1)
        direction = 1 if left_to_right else -1
        for x in xs:
            old = work[y, x]
            new = 1.0 if old >= 0.48 else 0.0
            out[y, x] = bool(new)
            err = old - new
            nx = x + direction
            if 0 <= nx < width:
                work[y, nx] += err * 7 / 16
            if y + 1 < height:
                if 0 <= x - direction < width:
                    work[y + 1, x - direction] += err * 3 / 16
                work[y + 1, x] += err * 5 / 16
                if 0 <= nx < width:
                    work[y + 1, nx] += err * 1 / 16
    return out


def extract_portrait_points(theme_name: str, seed: int = 42) -> np.ndarray:
    """Extract high-density, sharp dither points focused on Farah's face & upper body."""
    rng = np.random.default_rng(seed)
    source = Image.open(SOURCE).convert("RGB")
    w, h = source.size
    
    # Tight crop around Farah's face & upper body
    crop = source.crop((int(w * 0.15), int(h * 0.08), int(w * 0.85), int(h * 0.78)))
    crop = crop.resize((300, 340), Image.Resampling.LANCZOS)
    
    gray = ImageOps.grayscale(crop)
    
    # Background mask to eliminate noise outside the subject
    mask = np.ones((340, 300), dtype=bool)
    for y in range(340):
        for x in range(300):
            if x < 55 and y < 150:
                mask[y, x] = False
            if x > 250 and y < 120:
                mask[y, x] = False

    # Enhance facial feature contrast
    gray_img = ImageOps.autocontrast(gray, cutoff=1)
    gray_img = ImageEnhance.Contrast(gray_img).enhance(1.8)
    sharp = gray_img.filter(ImageFilter.UnsharpMask(radius=2, percent=240, threshold=1))
    
    bits = floyd_steinberg(np.asarray(sharp))
    active = ~bits & mask

    ys, xs = np.where(active)
    if len(xs) == 0:
        return np.zeros((0, 2), dtype=np.float32)

    # Offset to VISUAL.MAP box (x=74, y=154)
    points = np.column_stack((74 + xs, 154 + ys)).astype(np.float32)
    
    # High target density (3600 points for super crisp, sharp portrait)
    target_count = 3600
    if len(points) > target_count:
        indices = rng.choice(len(points), size=target_count, replace=False)
        points = points[indices]

    return points


def generate_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]
    rng = np.random.default_rng(314159)
    
    portrait_pts = extract_portrait_points(theme_name)
    N = len(portrait_pts)
    
    num_groups = 12
    group_size = N // num_groups
    
    path_groups_html = []
    
    for g in range(num_groups):
        idx_start = g * group_size
        idx_end = (g + 1) * group_size if g < num_groups - 1 else N
        
        g_port = portrait_pts[idx_start:idx_end]
        
        d_cmds = []
        for pt in g_port:
            x, y = int(round(pt[0])), int(round(pt[1]))
            d_cmds.append(f"M{x} {y}h1")
        path_d = "".join(d_cmds)
        
        # Fast, subtle particle motion offsets
        scatter_dx = float(rng.uniform(-14, 14))
        scatter_dy = float(rng.uniform(-16, 16))
        pulse_dx = float(rng.uniform(-8, 8))
        pulse_dy = float(rng.uniform(-10, 10))
        
        stroke_color = theme["portrait"] if g % 3 != 0 else theme["portrait_secondary"]
        
        # Keyframe timing (8.0s total):
        # 0s - 0.5s: Fast snap assembly into crisp portrait
        # 0.5s - 6.0s: SOLID CRISP PORTRAIT HOLD (80% of time)
        # 6.0s - 7.2s: Subtle live dot pulse wave
        # 7.2s - 8.0s: Fast snap back to crisp portrait
        path_html = f'''      <path d="{path_d}" fill="none" stroke="{stroke_color}" stroke-width="1.2" opacity="0.95">
        <animateTransform attributeName="transform" type="translate"
          begin="0s" dur="{LOOP_SECONDS}s" repeatCount="indefinite" calcMode="spline"
          keyTimes="0; 0.06; 0.75; 0.90; 1.0"
          keySplines="0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1"
          values="{scatter_dx:.1f} {scatter_dy:.1f}; 0 0; 0 0; {pulse_dx:.1f} {pulse_dy:.1f}; 0 0" />
        <animate attributeName="opacity"
          begin="0s" dur="{LOOP_SECONDS}s" repeatCount="indefinite"
          keyTimes="0; 0.06; 0.75; 0.90; 1.0"
          values="0.4; 0.95; 0.95; 0.85; 0.95" />
      </path>'''
        path_groups_html.append(path_html)

    paths_combined = "\n".join(path_groups_html)

    row_elements = []
    start_y = 148
    row_height = 34
    
    for i, (label, value) in enumerate(ROWS):
        y_pos = start_y + i * row_height
        is_grid = label.startswith("Grid.")
        label_col = theme["muted"] if not is_grid else theme["chrome"]
        val_col = theme["text"] if not is_grid else theme["portrait"]
        font_w = "700" if is_grid or label == "Subject" else "500"
        
        escaped_label = html.escape(label.upper())
        escaped_val = html.escape(value)
        
        row_elements.append(f'''    <g transform="translate(485, {y_pos})">
      <text x="0" y="0" fill="{label_col}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="12.5" font-weight="600">{escaped_label}</text>
      <text x="145" y="0" fill="{val_col}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="12.5" font-weight="{font_w}">{escaped_val}</text>
      <line x1="0" y1="10" x2="640" y2="10" stroke="{theme['line']}" stroke-width="0.5" opacity="0.4"/>
    </g>''')

    rows_svg = "\n".join(row_elements)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <clipPath id="visualClip">
      <rect x="49" y="124" width="390" height="414" rx="4"/>
    </clipPath>
  </defs>

  <!-- Canvas Background -->
  <rect width="{W}" height="{H}" rx="16" fill="{theme['bg']}"/>

  <!-- Main Terminal Box -->
  <rect x="14" y="14" width="1152" height="582" rx="12" fill="{theme['panel']}" stroke="{theme['line']}"/>
  
  <!-- Header Bar -->
  <path d="M14 62H1166" stroke="{theme['line']}"/>
  <circle cx="38" cy="38" r="6" fill="#FF5F57"/>
  <circle cx="59" cy="38" r="6" fill="#FEBC2E"/>
  <circle cx="80" cy="38" r="6" fill="#28C840"/>
  <text x="590" y="43" text-anchor="middle" fill="{theme['muted']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="600" letter-spacing="0.6">farah.sh --live</text>
  
  <rect x="1000" y="27" width="142" height="22" rx="11" fill="{theme['panel2']}" stroke="{theme['line']}"/>
  <circle cx="1014" cy="38" r="4" fill="{theme['accent']}"/>
  <text x="1026" y="42" fill="{theme['accent']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11" font-weight="700" letter-spacing="0.5">ONLINE · 100%</text>

  <!-- Left Frame: VISUAL.MAP -->
  <rect x="35" y="88" width="418" height="480" rx="6" fill="{theme['panel2']}" stroke="{theme['line']}"/>
  <path d="M35 124H453" stroke="{theme['line']}"/>
  <text x="49" y="111" fill="{theme['chrome']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">VISUAL.MAP</text>
  <text x="438" y="111" text-anchor="end" fill="{theme['muted']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">300×340 / 1-BIT DOT-MATRIX</text>

  <!-- Frame Corners -->
  <path d="M49 141h14M49 141v14M439 141h-14M439 141v14M49 539h14M49 539v-14M439 539h-14M439 539v-14" fill="none" stroke="{theme['chrome']}" opacity="0.6" stroke-width="1.5"/>

  <!-- Dithered Dot Matrix Portrait -->
  <g clip-path="url(#visualClip)" shape-rendering="crispEdges">
{paths_combined}
  </g>

  <!-- Right Frame: SYSTEM.PROFILE -->
  <rect x="468" y="88" width="676" height="480" rx="6" fill="{theme['panel2']}" stroke="{theme['line']}"/>
  <path d="M468 124H1144" stroke="{theme['line']}"/>
  <text x="485" y="111" fill="{theme['accent']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">SYSTEM.PROFILE</text>
  <text x="1127" y="111" text-anchor="end" fill="{theme['muted']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">LIVE TELEMETRY</text>

  <!-- Telemetry Content Rows -->
{rows_svg}

</svg>'''

    return svg_content


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    print("Generating banner-dark.svg...")
    dark_svg = generate_svg("dark")
    (ASSETS / "banner-dark.svg").write_text(dark_svg, encoding="utf-8")
    print(f"Wrote {ASSETS / 'banner-dark.svg'} ({len(dark_svg)} bytes)")

    print("Generating banner-light.svg...")
    light_svg = generate_svg("light")
    (ASSETS / "banner-light.svg").write_text(light_svg, encoding="utf-8")
    print(f"Wrote {ASSETS / 'banner-light.svg'} ({len(light_svg)} bytes)")

    print("Banner generation complete!")


if __name__ == "__main__":
    main()

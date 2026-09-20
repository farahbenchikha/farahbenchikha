#!/usr/bin/env python3
"""
Generate animated SVG GitHub profile banners for Farah Ben Chikha.
Style: Hexagonal Cloud Hologram / High-Tech Cyber HUD with photorealistic HD portrait.

Run from repository root:
    python scripts/banner/generate.py
"""

from __future__ import annotations
import base64
import html
import io
import math
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "farah-photo.jpeg"

W, H = 1180, 610

THEMES = {
    "dark": {
        "bg": "#070E1B",
        "panel": "#0B1528",
        "panel2": "#0F1C35",
        "line": "#1E2D4A",
        "muted": "#7C8BA1",
        "text": "#E2E8F0",
        "cyan": "#38BDF8",
        "purple": "#818CF8",
        "emerald": "#10B981",
        "pink": "#F43F5E",
        "badge_bg": "#162544",
    },
    "light": {
        "bg": "#F8FAFC",
        "panel": "#FFFFFF",
        "panel2": "#F1F5F9",
        "line": "#CBD5E1",
        "muted": "#64748B",
        "text": "#0F172A",
        "cyan": "#0284C7",
        "purple": "#6366F1",
        "emerald": "#059669",
        "pink": "#E11D48",
        "badge_bg": "#E2E8F0",
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


def prepare_photo_base64() -> str:
    """Crop and encode Farah's portrait into a sharp base64 JPEG."""
    source = Image.open(SOURCE).convert("RGB")
    w, h = source.size
    
    # Tight crop around Farah's face & shoulders
    crop = source.crop((int(w * 0.15), int(h * 0.05), int(w * 0.85), int(h * 0.75)))
    crop = crop.resize((360, 410), Image.Resampling.LANCZOS)
    
    # Enhance sharpness & vibrant contrast slightly for hologram frame
    crop = ImageEnhance.Contrast(crop).enhance(1.1)
    crop = ImageEnhance.Sharpness(crop).enhance(1.3)
    
    buf = io.BytesIO()
    crop.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def generate_svg(theme_name: str, b64_photo: str) -> str:
    theme = THEMES[theme_name]
    
    # Hexagon center and dimensions
    cx, cy = 244, 334
    
    # Generate Hexagon path points (radius R=155)
    r = 155
    hex_pts = []
    for i in range(6):
        a = i * math.pi / 3 - math.pi / 6
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        hex_pts.append(f"{x:.1f},{y:.1f}")
    hex_polygon_pts = " ".join(hex_pts)

    # Outer HUD Ring Hexagon points (radius R=172)
    r_outer = 172
    hex_outer_pts = []
    for i in range(6):
        a = i * math.pi / 3 - math.pi / 6
        x = cx + r_outer * math.cos(a)
        y = cy + r_outer * math.sin(a)
        hex_outer_pts.append(f"{x:.1f},{y:.1f}")
    hex_outer_polygon_pts = " ".join(hex_outer_pts)

    row_elements = []
    start_y = 148
    row_height = 34
    
    for i, (label, value) in enumerate(ROWS):
        y_pos = start_y + i * row_height
        is_grid = label.startswith("Grid.")
        label_col = theme["muted"] if not is_grid else theme["cyan"]
        val_col = theme["text"] if not is_grid else theme["cyan"]
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
    <!-- Hexagonal Clip Path for Photo -->
    <clipPath id="hexClip">
      <polygon points="{hex_polygon_pts}"/>
    </clipPath>

    <!-- Glowing Cyber Gradients -->
    <linearGradient id="cyberGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{theme['cyan']}"/>
      <stop offset="50%" stop-color="{theme['purple']}"/>
      <stop offset="100%" stop-color="{theme['emerald']}"/>
    </linearGradient>

    <linearGradient id="neonGlow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme['cyan']}" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="{theme['purple']}" stop-opacity="0.9"/>
    </linearGradient>
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
  <circle cx="1014" cy="38" r="4" fill="{theme['emerald']}"/>
  <text x="1026" y="42" fill="{theme['emerald']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11" font-weight="700" letter-spacing="0.5">ONLINE · 100%</text>

  <!-- Left Frame: HOLOGRAM.NODE -->
  <rect x="35" y="88" width="418" height="480" rx="6" fill="{theme['panel2']}" stroke="{theme['line']}"/>
  <path d="M35 124H453" stroke="{theme['line']}"/>
  <text x="49" y="111" fill="{theme['cyan']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">HOLOGRAM.NODE</text>
  <text x="438" y="111" text-anchor="end" fill="{theme['muted']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">HD PORTRAIT · CLOUD HUD</text>

  <!-- Frame Corners -->
  <path d="M49 141h14M49 141v14M439 141h-14M439 141v14M49 539h14M49 539v-14M439 539h-14M439 539v-14" fill="none" stroke="{theme['cyan']}" opacity="0.6" stroke-width="1.5"/>

  <!-- Outer HUD Hexagon Ring with Rotation Pulse Animation -->
  <polygon points="{hex_outer_polygon_pts}" fill="none" stroke="url(#cyberGrad)" stroke-width="1.5" stroke-dasharray="8 6" opacity="0.7">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="25s" repeatCount="indefinite"/>
  </polygon>

  <!-- Hexagonal Photo Portrait -->
  <g clip-path="url(#hexClip)">
    <image href="data:image/jpeg;base64,{b64_photo}" x="{cx - 180}" y="{cy - 205}" width="360" height="410" preserveAspectRatio="xMidYMid slice"/>
    
    <!-- Subtle Cyber Tint Overlay -->
    <polygon points="{hex_polygon_pts}" fill="{theme['cyan']}" opacity="0.05"/>
  </g>

  <!-- Inner Hexagon Neon Border -->
  <polygon points="{hex_polygon_pts}" fill="none" stroke="url(#neonGlow)" stroke-width="3"/>

  <!-- Tech Floating HUD Badges around Hexagon -->
  <g transform="translate({cx - 145}, {cy - 140})">
    <rect width="78" height="22" rx="11" fill="{theme['badge_bg']}" stroke="{theme['cyan']}" stroke-width="1"/>
    <text x="39" y="15" text-anchor="middle" fill="{theme['cyan']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10.5" font-weight="700">☸ Kubernetes</text>
  </g>

  <g transform="translate({cx + 70}, {cy - 140})">
    <rect width="72" height="22" rx="11" fill="{theme['badge_bg']}" stroke="{theme['purple']}" stroke-width="1"/>
    <text x="36" y="15" text-anchor="middle" fill="{theme['purple']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10.5" font-weight="700">☁️ Cloud</text>
  </g>

  <g transform="translate({cx - 145}, {cy + 120})">
    <rect width="82" height="22" rx="11" fill="{theme['badge_bg']}" stroke="{theme['emerald']}" stroke-width="1"/>
    <text x="41" y="15" text-anchor="middle" fill="{theme['emerald']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10.5" font-weight="700">🔐 DevSecOps</text>
  </g>

  <g transform="translate({cx + 65}, {cy + 120})">
    <rect width="68" height="22" rx="11" fill="{theme['badge_bg']}" stroke="{theme['cyan']}" stroke-width="1"/>
    <text x="34" y="15" text-anchor="middle" fill="{theme['cyan']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="10.5" font-weight="700">🤖 AIOps</text>
  </g>

  <!-- Live Pulse Dot at Hexagon Base -->
  <circle cx="{cx}" cy="{cy + 165}" r="4" fill="{theme['cyan']}">
    <animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>
  </circle>

  <!-- Right Frame: SYSTEM.PROFILE -->
  <rect x="468" y="88" width="676" height="480" rx="6" fill="{theme['panel2']}" stroke="{theme['line']}"/>
  <path d="M468 124H1144" stroke="{theme['line']}"/>
  <text x="485" y="111" fill="{theme['emerald']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="13" font-weight="700" letter-spacing="1.2">SYSTEM.PROFILE</text>
  <text x="1127" y="111" text-anchor="end" fill="{theme['muted']}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="11">LIVE TELEMETRY</text>

  <!-- Telemetry Content Rows -->
{rows_svg}

</svg>'''

    return svg_content


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    
    print("Preparing base64 photo encoding...")
    b64_photo = prepare_photo_base64()
    
    print("Generating banner-dark.svg (Hexagonal Hologram Cloud)...")
    dark_svg = generate_svg("dark", b64_photo)
    (ASSETS / "banner-dark.svg").write_text(dark_svg, encoding="utf-8")
    print(f"Wrote {ASSETS / 'banner-dark.svg'} ({len(dark_svg)} bytes)")

    print("Generating banner-light.svg (Hexagonal Hologram Cloud)...")
    light_svg = generate_svg("light", b64_photo)
    (ASSETS / "banner-light.svg").write_text(light_svg, encoding="utf-8")
    print(f"Wrote {ASSETS / 'banner-light.svg'} ({len(light_svg)} bytes)")

    print("Hexagonal Hologram Banner generation complete!")


if __name__ == "__main__":
    main()

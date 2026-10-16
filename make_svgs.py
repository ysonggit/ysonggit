"""Generate the profile README's SVGs: python3 make_svgs.py"""
import textwrap
from pathlib import Path

OUT = Path(__file__).parent / "assets"
ACCENT = "#d97757"

STYLE = """
<style>
  .fg { fill: #1f2328; } .mut { fill: #656d76; } .ln { stroke: #1f2328; } .bd { stroke: #d0d7de; }
  @media (prefers-color-scheme: dark) {
    .fg { fill: #e6edf3; } .mut { fill: #8d96a0; } .ln { stroke: #e6edf3; } .bd { stroke: #30363d; }
  }
  text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  .ln { fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
  .ac { fill: %s; } .acl { stroke: %s; fill: none; stroke-width: 2; stroke-linecap: round; }
  %s
</style>
"""

# Each icon is drawn in a 100x100 box; extra CSS animates it.
ICONS = {
    "touchbar": ("""
  <rect class="ln" x="4" y="30" width="92" height="40" rx="4"/>
  <rect class="ln" x="10" y="42" width="80" height="12" rx="3"/>
  <rect class="ac seg" x="12" y="44" width="14" height="8" rx="2"/>
  <line class="ln" x1="14" y1="62" x2="86" y2="62" stroke-dasharray="4 4"/>""",
     ".seg { animation: slide 3s ease-in-out infinite alternate; }"
     "@keyframes slide { from { transform: translateX(0); } to { transform: translateX(62px); } }"),
    "surface": ("""
  <rect class="ln" x="18" y="14" width="64" height="72" rx="10"/>
  <rect class="ln" x="28" y="24" width="44" height="30" rx="3"/>
  <circle class="ac led" cx="50" cy="39" r="4"/>
  <rect class="ln" x="28" y="64" width="18" height="10" rx="3"/>
  <rect class="ac" x="54" y="64" width="18" height="10" rx="3"/>""",
     ".led { animation: blink 1.6s ease-in-out infinite; }"
     "@keyframes blink { 50% { opacity: .15; } }"),
    "walkman": ("""
  <rect class="ln" x="6" y="22" width="88" height="56" rx="5"/>
  <rect class="ln" x="22" y="34" width="56" height="24" rx="12"/>
  <g class="reel" style="transform-origin: 35px 46px"><circle class="ln" cx="35" cy="46" r="7"/><line class="acl" x1="35" y1="39" x2="35" y2="53"/></g>
  <g class="reel" style="transform-origin: 65px 46px"><circle class="ln" cx="65" cy="46" r="7"/><line class="acl" x1="65" y1="39" x2="65" y2="53"/></g>
  <path class="ln" d="M26 78 L32 68 H68 L74 78"/>""",
     ".reel { animation: spin 2.4s linear infinite; }"
     "@keyframes spin { to { transform: rotate(360deg); } }"),
    "copilot": ("""
  <line class="ln" x1="4" y1="50" x2="96" y2="50" stroke-opacity=".15"/>
""" + "\n".join(
        f'  <rect class="ac bar" style="animation-delay:-{i * 0.17:.2f}s" x="{8 + i * 11}" y="30" width="5" height="40" rx="2.5"/>'
        for i in range(8)),
     ".bar { transform-box: fill-box; transform-origin: center; animation: talk 1.1s ease-in-out infinite; }"
     "@keyframes talk { 0%,100% { transform: scaleY(.2); } 50% { transform: scaleY(1); } }"),
    "capture": ("""
  <path class="ln" d="M8 32 H30 L36 22 H64 L70 32 H92 V80 H8 Z"/>
  <circle class="ln" cx="50" cy="54" r="15"/>
  <rect class="acl box" x="38" y="42" width="24" height="24" rx="2" stroke-dasharray="96"/>""",
     ".box { animation: draw 2.8s ease-in-out infinite; }"
     "@keyframes draw { 0% { stroke-dashoffset: 96; } 50%,80% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -96; } }"),
    "tracker": ("""
  <path class="ln" d="M8 14 V86 H94" stroke-opacity=".35"/>
  <path class="acl trend" d="M14 26 L30 34 L42 30 L56 50 L68 46 L88 72" stroke-dasharray="110"/>""",
     ".trend { animation: draw 3.2s ease-in-out infinite; }"
     "@keyframes draw { 0% { stroke-dashoffset: 110; } 60%,90% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 110; } }"),
    "insomnia": ("""
  <g transform="translate(3 3) scale(3.9)" style="stroke-width:.55">
  <g class="blink">
  <path class="ln" style="stroke-width:.55" d="M1.5 12 C7 4.5 17 4.5 22.5 12 C17 19.5 7 19.5 1.5 12 Z"/>
  <circle class="ac" cx="12" cy="12" r="4"/>
  </g>
  <path class="ln" style="stroke-width:.55" d="M4.55 6.2 L3.14 3.83 M8.26 4.62 L7.55 1.97 M12 4.13 L12 1.38 M15.74 4.62 L16.45 1.97 M19.45 6.2 L20.86 3.83"/>
  </g>""",
     ".blink { transform-box: fill-box; transform-origin: center; animation: blink 4s ease-in-out infinite; }"
     "@keyframes blink { 0%,88%,100% { transform: scaleY(1); } 93% { transform: scaleY(.08); } }"),
}

PROJECTS = [
    ("01", "claude-touchbar", "touchbar",
     "Claude Code's status and usage meters on a 2016 MacBook Pro Touch Bar under Linux. Tap to allow."),
    ("02", "agent-control-surface", "surface",
     "A small USB device by the keyboard. Shows what the agent is doing and takes Allow / Deny."),
    ("03", "pi-walkman", "walkman",
     "Spotify Connect on a Raspberry Pi, drawn as a cassette whose reels spin with the music."),
    ("04", "meeting-copilot", "copilot",
     "Live meeting transcription, German first, with answer suggestions. Audio never touches disk."),
    ("05", "rgb-d-capture", "capture",
     "Camera → vision model → human correction in the browser → labeled episodes."),
    ("06", "lean-tracker", "tracker",
     "Fasting, macros, training and skinfold body fat in one no-framework web app."),
    ("07", "insomnia-ubuntu", "insomnia",
     "Keeps an Ubuntu laptop awake for a set time, lid closed or not. An eye in the top bar counts down."),
]


def card(num, name, icon, desc):
    body, css = ICONS[icon]
    lines = textwrap.wrap(desc, 36)
    desc_svg = "\n".join(
        f'  <text class="mut" x="150" y="{104 + i * 19}" font-size="13">{l}</text>' for i, l in enumerate(lines))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 180" role="img" aria-label="{num} {name}: {desc}">
{STYLE % (ACCENT, ACCENT, css)}
  <rect class="bd" x="1" y="1" width="418" height="178" rx="10" fill="none"/>
  <g transform="translate(24 40)">{body}
  </g>
  <text class="mut mono" x="150" y="48" font-size="12">{num}</text>
  <text class="fg" x="150" y="76" font-size="18" font-weight="600">{name}</text>
{desc_svg}
</svg>
"""


# Header: a Touch Bar cycling through three states (thinking → running → asking).
HEADER = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 64" role="img" aria-label="ysonggit: a Touch Bar that asks Allow?">
<style>
  text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 15px; dominant-baseline: central; }}
  .t {{ fill: #e8e8e8; }} .d {{ fill: #8a8a8e; }} .k {{ fill: #2b2b2e; }} .a {{ fill: {ACCENT}; }}
  .s {{ opacity: 0; animation: cycle 9s infinite; }}
  .s2 {{ animation-delay: 3s; }} .s3 {{ animation-delay: 6s; }}
  @keyframes cycle {{ 0% {{ opacity: 0; }} 4%,30% {{ opacity: 1; }} 34%,100% {{ opacity: 0; }} }}
  .spin {{ transform-origin: 122px 32px; animation: spin 2s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  .pulse {{ animation: pulse 1s ease-in-out infinite alternate; }}
  @keyframes pulse {{ to {{ opacity: .55; }} }}
</style>
  <rect width="840" height="64" rx="12" fill="#0b0b0c"/>
  <rect class="k" x="8" y="8" width="80" height="48" rx="8"/>
  <text class="t" x="48" y="32" text-anchor="middle">esc</text>
  <text class="a spin" x="122" y="32" text-anchor="middle">✻</text>
  <text class="t" x="142" y="32">ysonggit</text>
  <g class="s"><text class="d" x="240" y="32">Thinking… building small things with agents</text></g>
  <g class="s s2"><text class="a" x="240" y="32">●</text><text class="t" x="260" y="32">Bash</text><text class="d" x="306" y="32">python3 walkman.py</text></g>
  <g class="s s3">
    <text class="d" x="574" y="32" text-anchor="end">Allow?</text>
    <rect class="k" x="588" y="8" width="118" height="48" rx="8"/><text class="d" x="647" y="32" text-anchor="middle">Deny</text>
    <rect class="a pulse" x="714" y="8" width="118" height="48" rx="8"/><text x="773" y="32" text-anchor="middle" fill="#0b0b0c">Allow</text>
  </g>
</svg>
"""

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "touchbar.svg").write_text(HEADER)
    for p in PROJECTS:
        (OUT / f"{p[0]}-{p[1]}.svg").write_text(card(*p))

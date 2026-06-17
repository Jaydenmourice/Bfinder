from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml import parse_xml
from lxml import etree

# ── App-exact palette ─────────────────────────────────────────────────────────
DARK_BG   = RGBColor(12,  16,  32)
PANEL_BG  = RGBColor(20,  28,  54)
CARD_BG   = RGBColor(26,  36,  68)
DEEP      = RGBColor(8,   11,  22)   # deeper than DARK_BG for gradient base
ACCENT    = RGBColor(0x4a, 0x9e, 0xff)
ACCENT_LT = RGBColor(0x7a, 0xb8, 0xff)
ACCENT_DM = RGBColor(0x1e, 0x5c, 0xcc)  # darker blue for gradient end
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
SILVER    = RGBColor(0xCC, 0xCC, 0xDD)
DIM       = RGBColor(0x88, 0x99, 0xBB)

LOGO = r"C:\Users\HP\Desktop\Bfinder\images\logo.png"

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]


# ── Helpers ───────────────────────────────────────────────────────────────────

def add_slide():
    return prs.slides.add_slide(blank)


def _rgb_hex(c):
    return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"


def set_gradient(shape, c1, c2, angle_deg=135, angle=None):
    """Replace shape fill with a two-stop linear gradient."""
    if angle is not None:
        angle_deg = angle
    spPr = shape._element.spPr
    # remove any existing fill child
    for tag in ('a:solidFill', 'a:gradFill', 'a:noFill', 'a:blipFill', 'a:pattFill'):
        el = spPr.find(qn(tag))
        if el is not None:
            spPr.remove(el)

    ang = str(int(angle_deg * 60000) % 21600000)
    xml = f"""<a:gradFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <a:gsLst>
    <a:gs pos="0"><a:srgbClr val="{_rgb_hex(c1)}"/></a:gs>
    <a:gs pos="100000"><a:srgbClr val="{_rgb_hex(c2)}"/></a:gs>
  </a:gsLst>
  <a:lin ang="{ang}" scaled="0"/>
</a:gradFill>"""
    spPr.append(parse_xml(xml))


def solid_box(slide, l, t, w, h, fill=PANEL_BG, border=None, bw=0.75):
    shp = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if border:
        shp.line.color.rgb = border
        shp.line.width = Pt(bw)
    else:
        shp.line.fill.background()
    return shp


def grad_box(slide, l, t, w, h, c1, c2, angle=135, border=None, bw=0.75):
    shp = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shp.fill.solid()          # placeholder, replaced below
    shp.fill.fore_color.rgb = c1
    set_gradient(shp, c1, c2, angle)
    if border:
        shp.line.color.rgb = border
        shp.line.width = Pt(bw)
    else:
        shp.line.fill.background()
    return shp


def line(slide, l, t, w, color=ACCENT, thickness=0.04):
    """Thin decorative horizontal line."""
    solid_box(slide, l, t, w, thickness, fill=color)


def txt(slide, text, l, t, w, h, size=16, bold=False, color=WHITE,
        align=PP_ALIGN.LEFT, italic=False, wrap=True):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tb.word_wrap = wrap
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return tb


def logo_img(slide, l, t, w, h):
    slide.shapes.add_picture(LOGO, Inches(l), Inches(t), Inches(w), Inches(h))


def slide_header(slide, title):
    """Consistent luxury header: logo + title + thin underline."""
    logo_img(slide, 0.38, 0.15, 0.72, 0.72)
    txt(slide, title, 1.28, 0.18, 11.5, 0.72, size=30, bold=True, color=WHITE)
    line(slide, 0.38, 0.98, 12.57, color=ACCENT, thickness=0.03)
    # subtle fade line below
    line(slide, 0.38, 1.04, 12.57, color=ACCENT_DM, thickness=0.015)


def page_num(slide, n):
    txt(slide, f"{n} / 11", 12.2, 7.1, 1.0, 0.3, size=10,
        color=DIM, align=PP_ALIGN.RIGHT)


# ── BG helper (dark gradient across whole slide) ─────────────────────────────
def luxury_bg(slide):
    shp = slide.shapes.add_shape(1, 0, 0,
                                 prs.slide_width, prs.slide_height)
    set_gradient(shp, DEEP, DARK_BG, angle=150)
    shp.line.fill.background()
    # very subtle vignette panel at top
    vign = slide.shapes.add_shape(1, 0, 0, prs.slide_width, Inches(1.15))
    set_gradient(vign, RGBColor(10,14,30), DEEP, angle=180)
    vign.line.fill.background()


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 1  ·  Title
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)

# Central glass panel
grad_box(s, 1.2, 1.55, 10.9, 4.4,
         RGBColor(18,26,52), RGBColor(10,15,32), angle=135,
         border=ACCENT_DM, bw=0.5)
# top accent line on panel
line(s, 1.2, 1.55, 10.9, color=ACCENT, thickness=0.055)
line(s, 1.2, 5.9,  10.9, color=ACCENT, thickness=0.055)

logo_img(s, 2.0, 1.85, 1.55, 1.55)

txt(s, "BFINDER", 3.8, 1.75, 8.2, 1.5,
    size=70, bold=True, color=ACCENT)
txt(s, "Web Security Vulnerability Scanner", 3.8, 3.25, 8.2, 0.7,
    size=22, color=WHITE)

# thin separator
line(s, 3.8, 4.05, 8.2, color=ACCENT_DM, thickness=0.02)

txt(s, "Presenter: Jayden  ·  June 2026", 3.8, 4.18, 8.2, 0.45,
    size=14, color=SILVER, italic=True)
txt(s, "Supervisor Presentation", 3.8, 4.72, 8.2, 0.45,
    size=12, color=DIM, italic=True)

# corner accent dots
for cx, cy in [(1.2, 1.55), (12.1, 1.55), (1.2, 5.9), (12.1, 5.9)]:
    solid_box(s, cx-0.06, cy-0.06, 0.12, 0.12, fill=ACCENT)

page_num(s, 1)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 2  ·  Agenda
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "AGENDA")

items = [
    ("01", "Problem Statement"),
    ("02", "What is Bfinder?"),
    ("03", "Key Features"),
    ("04", "System Architecture"),
    ("05", "Live Demo Overview"),
    ("06", "Technical Stack"),
    ("07", "Future Roadmap"),
    ("08", "Q & A"),
]
for i, (num, label) in enumerate(items):
    cx = 0.38 if i < 4 else 6.88
    cy = 1.2 + (i % 4) * 1.5
    grad_box(s, cx, cy, 6.0, 1.2,
             RGBColor(20,28,54), RGBColor(12,18,40), angle=135,
             border=ACCENT_DM, bw=0.5)
    line(s, cx, cy, 6.0, color=ACCENT, thickness=0.04)
    txt(s, num,   cx+0.18, cy+0.35, 0.7, 0.55, size=13, bold=True, color=ACCENT)
    txt(s, label, cx+0.85, cy+0.32, 5.0, 0.6,  size=16, color=WHITE)

page_num(s, 2)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 3  ·  Problem Statement
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Problem Statement")

problems = [
    ("Security vulnerabilities slip to production",
     "Developers focus on features; security checks are often skipped or done too late."),
    ("Manual code review is slow & inconsistent",
     "Human reviewers miss subtle issues — XSS, SQL injection, and exposed secrets."),
    ("No lightweight desktop tool for offline scanning",
     "Existing tools are cloud-dependent, expensive, or require DevOps-level setup."),
]
for i, (title, desc) in enumerate(problems):
    y = 1.22 + i * 1.95
    grad_box(s, 0.38, y, 12.57, 1.7,
             RGBColor(22,30,58), RGBColor(12,17,36), angle=135,
             border=ACCENT_DM, bw=0.5)
    line(s, 0.38, y, 0.055, color=ACCENT, thickness=1.7)   # left thin bar
    txt(s, title, 0.68, y+0.15, 11.9, 0.55, size=17, bold=True, color=WHITE)
    txt(s, desc,  0.68, y+0.75, 11.9, 0.75, size=13, color=SILVER)

page_num(s, 3)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 4  ·  What is Bfinder?
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "What is Bfinder?")

# Left panel
grad_box(s, 0.38, 1.2, 6.0, 5.9,
         RGBColor(20,28,54), RGBColor(10,15,32), angle=150,
         border=ACCENT_DM, bw=0.5)
line(s, 0.38, 1.2, 6.0, color=ACCENT, thickness=0.04)
txt(s, "About", 0.6, 1.32, 5.6, 0.5, size=11, bold=True, color=ACCENT_LT)
txt(s,
    "Bfinder is a desktop application that automatically scans "
    "web project directories for common security vulnerabilities — "
    "giving developers instant, actionable results before deployment.",
    0.6, 1.82, 5.6, 2.0, size=13, color=WHITE)
line(s, 0.6, 3.7, 5.6, color=ACCENT_DM, thickness=0.02)
txt(s, "Target Users", 0.6, 3.85, 5.6, 0.42, size=11, bold=True, color=ACCENT_LT)
for i, u in enumerate(["Web Developers", "QA Engineers",
                        "Security Auditors", "CS Students"]):
    txt(s, f"— {u}", 0.75, 4.3+i*0.65, 5.5, 0.5, size=13, color=SILVER)

# Right panel
grad_box(s, 7.0, 1.2, 5.95, 5.9,
         RGBColor(20,28,54), RGBColor(10,15,32), angle=150,
         border=ACCENT_DM, bw=0.5)
line(s, 7.0, 1.2, 5.95, color=ACCENT, thickness=0.04)
txt(s, "Goals", 7.2, 1.32, 5.5, 0.5, size=11, bold=True, color=ACCENT_LT)
goals = [
    "Detect vulnerabilities early in development",
    "Work fully offline — no internet needed",
    "Simple UI any developer can use",
    "Generate printable encrypted PDF reports",
    "Track scan history across 50 scans",
]
for i, g in enumerate(goals):
    line(s, 7.25, 1.9+i*1.0, 0.3, color=ACCENT, thickness=0.03)
    txt(s, g, 7.7, 1.83+i*1.0, 5.1, 0.65, size=13, color=WHITE)

page_num(s, 4)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 5  ·  Key Features
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Key Features")

features = [
    ("Vulnerability Scanner",  "Scans .html .js .ts .php .css .json .env .xml .sql"),
    ("Login & Auth",           "Secure login with OS keyring password and logout"),
    ("Bug Explanations",       "Every issue includes a description and fix suggestion"),
    ("PDF Reports",            "Generates encrypted PDF reports of all findings"),
    ("Scan History",           "Last 50 scans stored and viewable on the History page"),
    ("Security Tips",          "Rotating security tips shown on the home page"),
]
positions = [(0.38,1.18),(4.65,1.18),(8.92,1.18),
             (0.38,4.05),(4.65,4.05),(8.92,4.05)]
for (cx, cy), (ft, fd) in zip(positions, features):
    grad_box(s, cx, cy, 3.9, 2.65,
             RGBColor(22,30,58), RGBColor(12,18,38), angle=135,
             border=ACCENT_DM, bw=0.5)
    line(s, cx, cy, 3.9, color=ACCENT, thickness=0.04)
    txt(s, ft, cx+0.2, cy+0.2,  3.5, 0.55, size=14, bold=True, color=ACCENT_LT)
    line(s, cx+0.2, cy+0.82, 3.5, color=ACCENT_DM, thickness=0.018)
    txt(s, fd, cx+0.2, cy+0.95, 3.5, 1.55, size=12, color=SILVER)

page_num(s, 5)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 6  ·  System Architecture
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "System Architecture")

layers = [
    ("UI Layer (PyQt5)",       "LoginDialog  ·  BfinderWindow  ·  QStackedWidget Pages",
     ACCENT,    RGBColor(0x1a, 0x50, 0xcc)),
    ("Logic Layer",            "bug_exp.py — scan engine  ·  sec_tip.py — security tips",
     ACCENT_LT, RGBColor(0x30, 0x60, 0xaa)),
    ("Data Layer",             "scan_history.json  ·  contact_info.json  ·  PDF Reports",
     RGBColor(0x50,0xa8,0xff), RGBColor(0x18,0x38,0x80)),
    ("OS / Security Layer",    "keyring (password)  ·  xhtml2pdf + PyPDF2 (encryption)",
     RGBColor(0x30,0x80,0xee), RGBColor(0x10,0x28,0x66)),
]
for i, (title, detail, c1, c2) in enumerate(layers):
    y = 1.2 + i * 1.5
    grad_box(s, 0.38, y, 12.57, 1.28,
             RGBColor(18,25,50), RGBColor(10,14,32), angle=135,
             border=ACCENT_DM, bw=0.5)
    # label box — gradient
    grad_box(s, 0.38, y, 3.3, 1.28, c2, c1, angle=135)
    txt(s, title,  0.58, y+0.38, 3.0, 0.55, size=13, bold=True, color=WHITE)
    txt(s, detail, 3.85, y+0.38, 9.0, 0.55, size=13, color=SILVER)

page_num(s, 6)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 7  ·  Supported File Types
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Supported File Types")

types = [
    (".html",    "XSS, inline scripts, unsafe forms"),
    (".js / .ts","eval(), dangerous sinks, exposed keys"),
    (".php",     "SQL injection, exec(), file inclusion"),
    (".env",     "Exposed secrets, API keys, passwords"),
    (".sql",     "Unsafe queries, DROP/TRUNCATE risks"),
    (".json",    "Hardcoded credentials, insecure configs"),
    (".css",     "CSS injection, expression() exploits"),
    (".xml",     "XXE injection, external entity refs"),
]
for i, (ext, desc) in enumerate(types):
    cx = 0.38 if i < 4 else 6.88
    cy = 1.18 + (i % 4) * 1.57
    grad_box(s, cx, cy, 6.0, 1.34,
             RGBColor(20,28,54), RGBColor(10,15,32), angle=135,
             border=ACCENT_DM, bw=0.5)
    line(s, cx, cy, 6.0, color=ACCENT, thickness=0.04)
    txt(s, ext,  cx+0.2, cy+0.15, 1.6, 0.55, size=15, bold=True, color=ACCENT)
    txt(s, desc, cx+2.0, cy+0.17, 3.8, 0.78, size=12, color=SILVER)

page_num(s, 7)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 8  ·  Technical Stack
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Technical Stack")

stack = [
    ("Python 3",    "Core language — cross-platform, rich ecosystem"),
    ("PyQt5",       "Desktop UI framework — windows, widgets, event loop"),
    ("keyring",     "OS-native secure credential storage"),
    ("xhtml2pdf",   "HTML-to-PDF conversion for report generation"),
    ("PyPDF2",      "PDF encryption and manipulation"),
    ("JSON",        "Lightweight local storage for history and settings"),
]
for i, (tech, desc) in enumerate(stack):
    y = 1.18 + i * 1.03
    grad_box(s, 0.38, y, 12.57, 0.85,
             RGBColor(18,25,50), RGBColor(10,14,32), angle=135,
             border=ACCENT_DM, bw=0.5)
    grad_box(s, 0.38, y, 2.6, 0.85,
             ACCENT_DM, RGBColor(0x10, 0x30, 0x80), angle=135)
    txt(s, tech, 0.55, y+0.2, 2.3, 0.48, size=13, bold=True, color=WHITE)
    txt(s, desc, 3.2,  y+0.2, 9.5, 0.48, size=13, color=SILVER)

page_num(s, 8)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 9  ·  Demo Overview
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Demo Overview")

steps = [
    ("1", "Launch Bfinder",        "Enter password to unlock the application"),
    ("2", "Browse Project Folder", "Select a web project directory to scan"),
    ("3", "Run Scan",              "Click Scan — Bfinder analyses all supported files"),
    ("4", "Review Results",        "View detected bugs with explanations on Home page"),
    ("5", "Generate Report",       "Click Print Report to produce an encrypted PDF"),
    ("6", "Check History",         "Navigate to History to review previous scans"),
]
for i, (num, title, desc) in enumerate(steps):
    cx = 0.38 if i < 3 else 6.88
    cy = 1.18 + (i % 3) * 2.1
    grad_box(s, cx, cy, 6.0, 1.85,
             RGBColor(20,28,54), RGBColor(10,15,32), angle=135,
             border=ACCENT_DM, bw=0.5)
    line(s, cx, cy, 6.0, color=ACCENT, thickness=0.04)
    # step circle/number
    solid_box(s, cx+0.22, cy+0.55, 0.62, 0.62, fill=ACCENT_DM, border=ACCENT, bw=0.75)
    txt(s, num,   cx+0.22, cy+0.58, 0.62, 0.55,
        size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txt(s, title, cx+1.05, cy+0.18, 4.75, 0.55, size=14, bold=True, color=ACCENT_LT)
    txt(s, desc,  cx+1.05, cy+0.82, 4.75, 0.85, size=12, color=SILVER)

page_num(s, 9)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 10  ·  Future Roadmap
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)
slide_header(s, "Future Roadmap")

phases = [
    ("Phase 1", "Short Term",
     ["More scan rules & patterns",
      "Support additional file types",
      "Better bug explanation detail"],
     ACCENT,    ACCENT_DM),
    ("Phase 2", "Mid Term",
     ["CI/CD pipeline integration",
      "Command-line interface (CLI)",
      "Team-shared scan history"],
     ACCENT_LT, RGBColor(0x30,0x60,0xaa)),
    ("Phase 3", "Long Term",
     ["Web / cloud-based version",
      "AI-powered fix suggestions",
      "Real-time scan as-you-type"],
     RGBColor(0x50,0xa8,0xff), RGBColor(0x18,0x38,0x80)),
]
for i, (phase, timeline, items, c1, c2) in enumerate(phases):
    x = 0.38 + i * 4.3
    grad_box(s, x, 1.18, 3.9, 5.95,
             RGBColor(18,25,50), RGBColor(10,14,32), angle=150,
             border=ACCENT_DM, bw=0.5)
    grad_box(s, x, 1.18, 3.9, 1.2, c2, c1, angle=135)
    txt(s, phase,    x+0.15, 1.24, 3.6, 0.55, size=16, bold=True, color=WHITE)
    txt(s, timeline, x+0.15, 1.76, 3.6, 0.42, size=11, color=WHITE, italic=True)
    for j, item in enumerate(items):
        line(s, x+0.28, 2.6+j*1.4, 0.35, color=c1, thickness=0.03)
        txt(s, item, x+0.78, 2.55+j*1.4, 3.0, 0.75, size=12, color=SILVER)

page_num(s, 10)

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE 11  ·  Thank You
# ═══════════════════════════════════════════════════════════════════════════════
s = add_slide()
luxury_bg(s)

# Central panel
grad_box(s, 1.5, 1.65, 10.33, 4.2,
         RGBColor(18,26,52), RGBColor(8,12,26), angle=135,
         border=ACCENT_DM, bw=0.5)
line(s, 1.5, 1.65,  10.33, color=ACCENT, thickness=0.055)
line(s, 1.5, 5.8,   10.33, color=ACCENT, thickness=0.055)

logo_img(s, 2.2, 2.0, 1.55, 1.55)

txt(s, "Thank You", 4.0, 1.85, 7.7, 1.5,
    size=60, bold=True, color=ACCENT)
txt(s, "Questions & Discussion", 4.0, 3.38, 7.7, 0.7, size=21, color=WHITE)

line(s, 4.0, 4.18, 7.7, color=ACCENT_DM, thickness=0.02)

txt(s, "Jayden  ·  waltermkingilima96@gmail.com",
    4.0, 4.32, 7.7, 0.48, size=14, color=ACCENT_LT, italic=True)
txt(s, "Bfinder  ·  Web Security Scanner  ·  June 2026",
    0, 6.4, 13.33, 0.4, size=11, color=DIM,
    align=PP_ALIGN.CENTER, italic=True)

# corner accents
for cx, cy in [(1.5, 1.65),(11.83, 1.65),(1.5, 5.8),(11.83, 5.8)]:
    solid_box(s, cx-0.07, cy-0.07, 0.14, 0.14, fill=ACCENT)

page_num(s, 11)

# ── Save ──────────────────────────────────────────────────────────────────────
out = r"C:\Users\HP\Desktop\Bfinder\Bfinder_Presentation_v2.pptx"
prs.save(out)
print(f"Saved: {out}")

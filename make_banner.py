from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 300
PAPER = (250, 250, 249)
INK = (31, 41, 55)
MUTED = (100, 116, 139)
TEAL = (15, 118, 110)
CORAL = (194, 65, 12)
INDIGO = (67, 56, 202)

img = Image.new("RGB", (W, H), PAPER)
draw = ImageDraw.Draw(img)

mono_bold = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
mono = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
sans_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

title_font = ImageFont.truetype(sans_bold, 44)
subtitle_font = ImageFont.truetype(mono, 19)
code_font = ImageFont.truetype(mono, 15)

def center_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)

draw.rectangle([0, 0, W, 36], fill=INK)
for i, c in enumerate([CORAL, (219, 171, 9), TEAL]):
    draw.ellipse([20 + i * 22, 12, 20 + i * 22 + 12, 24], fill=c)
draw.text((90, 10), "queries.sql", font=code_font, fill=(220, 220, 220))

center_text(draw, "SQL BUSINESS INSIGHTS DASHBOARD", 76, title_font, INK)
center_text(draw, "SELECT insights FROM sales_data  --  for management decisions", 138, subtitle_font, TEAL)

tags = ["JOIN", "GROUP BY", "HAVING", "CASE", "WINDOW FUNCTIONS"]
tag_font = ImageFont.truetype(mono_bold, 14)
gap = 16
widths = []
for t in tags:
    bbox = draw.textbbox((0, 0), t, font=tag_font)
    widths.append(bbox[2] - bbox[0] + 28)
total_w = sum(widths) + gap * (len(tags) - 1)
x = (W - total_w) / 2
y_pill = 195
colors = [TEAL, INDIGO, CORAL, TEAL, INDIGO]
for t, w, c in zip(tags, widths, colors):
    draw.rounded_rectangle([x, y_pill, x + w, y_pill + 32], radius=16, outline=c, width=2)
    bbox = draw.textbbox((0, 0), t, font=tag_font)
    tw = bbox[2] - bbox[0]
    draw.text((x + (w - tw) / 2, y_pill + 8), t, font=tag_font, fill=c)
    x += w + gap

center_text(draw, "Retail Sales Analysis  \u00b7  Customer Segmentation  \u00b7  Revenue Growth", 250,
            ImageFont.truetype(mono, 14), MUTED)

img.save("/home/claude/sql-business-insights-dashboard/screenshots/banner.png")
print("Banner saved.")

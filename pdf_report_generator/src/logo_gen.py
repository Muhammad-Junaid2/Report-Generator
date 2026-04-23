"""
Generate a simple logo image for branding.
"""
from PIL import Image, ImageDraw, ImageFont
import os


def create_logo(path: str, report_type: str = "student"):
    """Generate a simple logo PNG for the report header."""
    width, height = 300, 80
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    if report_type == "student":
        color = (13, 71, 161)       # Deep blue
        accent = (21, 101, 192)
        label = "EDU"
        subtitle = "Academic Portal"
    else:
        color = (27, 94, 32)        # Deep green
        accent = (46, 125, 50)
        label = "BIZ"
        subtitle = "Corporate Portal"

    # Draw rounded rectangle background
    draw.rounded_rectangle([0, 0, width - 1, height - 1], radius=12, fill=color)

    # Left badge
    draw.rounded_rectangle([8, 8, 64, height - 8], radius=8, fill=accent)

    # Try to use a font, fall back to default
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = font_big
        font_sub = font_big

    # Badge text
    draw.text((18, 22), label, fill="white", font=font_big)

    # Main text
    draw.text((76, 14), "ReportGen Pro", fill="white", font=font_small)
    draw.text((76, 38), subtitle, fill=(200, 230, 255) if report_type == "student" else (200, 255, 200), font=font_sub)

    # Decorative line
    draw.line([76, 34, width - 12, 34], fill=(255, 255, 255, 80), width=1)

    img.save(path, "PNG")
    return path


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    create_logo("assets/logo_student.png", "student")
    create_logo("assets/logo_company.png", "company")
    print("Logos created.")

"""Generate error images with PIL default bitmap font.

Renders error message (red) + rejected prompt on black background.
Resolution sourced from profile parameters with 1024x1024 fallback.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple


FALLBACK_WIDTH = 1024
FALLBACK_HEIGHT = 1024


def get_image_resolution(params: Dict[str, Any]) -> Tuple[int, int]:
    """Extract width/height from parameters, falling back to 1024x1024."""
    width = params.get("width") or FALLBACK_WIDTH
    height = params.get("height") or FALLBACK_HEIGHT
    return int(width), int(height)


def generate_error_image(
    error_message: str, prompt: str, width: int, height: int
) -> Image.Image:
    """Render error message and rejected prompt as red text on black background."""
    img = Image.new("RGB", (width, height), color="black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    char_width = 8

    lines: list[str] = ["=== ERROR ===", ""]
    lines.append(f"Error: {error_message}")
    lines.append("")
    lines.append("=== REJECTED PROMPT ===")
    lines.append("")

    max_chars = width // char_width
    for word in prompt.split():
        if not lines or len(lines[-1]) + len(word) + 1 > max_chars:
            lines.append(word)
        else:
            lines[-1] = f"{lines[-1]} {word}"
    lines.append("")

    y = 20
    for line in lines:
        draw.text((10, y), line, fill="red", font=font)
        y += 12
        if y > height - 20:
            break

    return img

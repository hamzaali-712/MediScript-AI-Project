"""
MediScript AI — Image Processor
Enhances prescription photo quality before sending to Gemini Vision.
Better image = more accurate drug extraction.
"""

from PIL import Image, ImageEnhance, ImageFilter
import io


def enhance_image(image_bytes: bytes) -> bytes:
    """
    Enhance prescription image quality:
    - Upscale if too small
    - Boost contrast (makes text stand out)
    - Sharpen (clarifies blurry handwriting)
    - Apply SHARPEN filter
    Returns enhanced image bytes.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Upscale if too small (Gemini works better with larger images)
        min_size = 1000
        if min(img.size) < min_size:
            ratio = min_size / min(img.size)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        # Enhance contrast (makes text darker, background lighter)
        img = ImageEnhance.Contrast(img).enhance(2.0)

        # Enhance sharpness (clears blurry handwriting)
        img = ImageEnhance.Sharpness(img).enhance(2.5)

        # Apply sharpen filter
        img = img.filter(ImageFilter.SHARPEN)

        # Re-encode to JPEG with high quality
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue()

    except Exception as e:
        print(f"[ImageProcessor] Enhancement failed: {e} — using original image")
        return image_bytes  # Return original if enhancement fails


def get_image_info(image_bytes: bytes) -> dict:
    """Return basic image metadata."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_kb": round(len(image_bytes) / 1024, 1),
        }
    except Exception:
        return {}

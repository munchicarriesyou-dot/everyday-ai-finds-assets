"""Generate a deterministic, date-stamped Instagram asset and caption."""
import argparse
import json
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

def generate(day=None, root="images"):
    today = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()
    date = today if day is None else __import__("datetime").date.fromisoformat(day)
    if date > today + timedelta(days=1):
        raise ValueError("Cannot generate more than one day in advance")
    topics = json.loads(Path("data/topics.json").read_text(encoding="utf-8"))
    topic = topics[date.toordinal() % len(topics)]
    output = Path(root) / date.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    image_path = output / "post.jpg"
    caption = "\n\n".join([topic["title"], topic["tip"], topic["cta"],
        "#AITools #ArtificialIntelligence #Productivity #AITips"])
    image = Image.new("RGB", (1080, 1350), "#101827")
    draw = ImageDraw.Draw(image)
    bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 62)
    regular = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 37)
    draw.text((75, 90), "EVERYDAY AI FINDS", font=regular, fill="#5ce1cf")
    y = 300
    for line in textwrap.wrap(topic["title"].upper(), width=22):
        draw.text((75, y), line, font=bold, fill="white")
        y += 92
    y = 730
    for line in textwrap.wrap(topic["tip"], width=43):
        draw.text((75, y), line, font=regular, fill="#e1ebf5")
        y += 62
    draw.text((75, 1210), "@everydayaifinds99", font=regular, fill="#5ce1cf")
    image.save(image_path, format="JPEG", quality=92)
    manifest = {"date": date.isoformat(), "image": "post.jpg", "caption": caption}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Generated date:", date.isoformat())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date")
    args = parser.parse_args()
    generate(args.date)

"""Generate a deterministic, date-stamped Instagram asset and caption."""
import argparse
import random
import json
import textwrap
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

def research_topics():
    """Read primary-source arXiv RSS titles. No invented claims or numerical statistics."""
    request = urllib.request.Request(
        "https://rss.arxiv.org/rss/cs.AI", headers={"User-Agent": "EverydayAIFinds/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            root = ET.fromstring(response.read(500000))
    except (OSError, ValueError, ET.ParseError) as exc:
        print("Research feed unavailable; using curated evergreen content:", type(exc).__name__)
        return []
    results = []
    for item in root.findall(".//item"):
        title = " ".join((item.findtext("title") or "").split())
        link = (item.findtext("link") or "").strip()
        match = re.fullmatch(r"https?://(?:www\\.)?arxiv\\.org/abs/([0-9.]+|[a-z-]+/[0-9]+)(?:v[0-9]+)?", link)
        if not match or not (12 <= len(title) <= 180):
            continue
        paper_id = match.group(1)
        results.append({
            "id": "arxiv-" + paper_id.replace("/", "-"),
            "category": "research",
            "title": "AI research spotlight",
            "tip": "Researchers are exploring: " + title[:90] + ("..." if len(title) > 90 else ""),
            "cta": "Read the original paper before drawing conclusions.",
            "source_url": link,
            "paper_title": title,
        })
    return results

def render_story(topic, output):
    image = Image.new("RGB", (1080, 1920), "#101827")
    draw = ImageDraw.Draw(image)
    def block(text, top, bottom, size, bold=False, color="white"):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf"
        for n in range(size, 23, -2):
            font = ImageFont.truetype(font_path, n)
            lines = []
            line = ""
            for word in text.split():
                candidate = (line + " " + word).strip()
                if draw.textlength(candidate, font=font) > 840 and line:
                    lines.append(line)
                    line = word
                else:
                    line = candidate
            if line:
                lines.append(line)
            spacing = int(n * 0.35)
            value = "\n".join(lines)
            bbox = draw.multiline_textbbox((0, 0), value, font=font, spacing=spacing)
            if bbox[2]-bbox[0] <= 840 and bbox[3]-bbox[1] <= bottom-top:
                draw.multiline_text((120-bbox[0], top-bbox[1]), value, font=font, spacing=spacing, fill=color)
                return
        raise ValueError("Story text cannot fit safe area")
    block("EVERYDAY AI FINDS", 270, 340, 38, color="#5ce1cf")
    draw.rounded_rectangle((120, 375, 960, 383), radius=4, fill="#5ce1cf")
    block(topic["title"].upper(), 450, 850, 88, True)
    block(topic["tip"], 920, 1390, 55, color="#e1ebf5")
    # The footer already displays the account handle; avoid repeating it in the CTA.
    story_cta = re.sub(r"@everydayaifinds99\b", "us", topic["cta"], flags=re.IGNORECASE)
    block(story_cta, 1450, 1580, 38, color="#5ce1cf")
    block("@everydayaifinds99", 1600, 1660, 34, color="#5ce1cf")
    image.save(output / "story.jpg", format="JPEG", quality=94)

def choose_topic(candidates, date):
    from editorial_policy import choose
    policy = json.loads(Path("data/editorial-policy.json").read_text())
    return choose(candidates, policy, random.Random(date.toordinal()))

def generate(day=None, root="images"):
    today = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date()
    date = today if day is None else __import__("datetime").date.fromisoformat(day)
    if date > today + timedelta(days=1):
        raise ValueError("Cannot generate more than one day in advance")
    topics = json.loads(Path("data/topics.json").read_text(encoding="utf-8"))
    # Every dated manifest records its source ID. Never recycle a published topic.
    used = set()
    for old in Path(root).glob("*/manifest.json"):
        try:
            prior = json.loads(old.read_text(encoding="utf-8"))
            if prior.get("date") != date.isoformat():
                used.add(prior.get("content_id"))
        except (OSError, ValueError):
            continue
    existing = Path(root) / date.isoformat() / "manifest.json"
    if existing.exists():
        prior = json.loads(existing.read_text(encoding="utf-8"))
        topic = next((t for t in topics if t["id"] == prior.get("content_id")), None)
        if topic is None and isinstance(prior.get("topic_snapshot"), dict):
            snapshot = prior["topic_snapshot"]
            if snapshot.get("id") == prior.get("content_id") and all(snapshot.get(k) for k in ("category", "title", "tip", "cta")):
                topic = snapshot
        if topic is None:
            raise RuntimeError("Existing daily topic is missing; refuse to silently change it")
    else:
        research = [t for t in research_topics() if t["id"] not in used]
        candidates = [t for t in topics if t["id"] not in used] + research
        if not candidates:
            raise RuntimeError("Content library exhausted: refusing to repeat an old post")
        topic = next((t for t in candidates if t["id"] == "accessible-ai-all-ages" and date.isoformat() == "2026-11-24"), None) or choose_topic(candidates, date)
    output = Path(root) / date.isoformat()
    output.mkdir(parents=True, exist_ok=True)
    image_path = output / "post.jpg"
    caption = "\n\n".join([topic["title"], topic["tip"], topic["cta"],
        "#AITools #ArtificialIntelligence #Productivity #AITips"])
    if topic.get("source_url"):
        caption += "\n\nPrimary source: " + topic["source_url"]
        caption += "\nPaper: " + topic["paper_title"]
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
    render_story(topic, output)
    manifest = {"date": date.isoformat(), "content_id": topic["id"], "category": topic["category"], "topic_snapshot": topic, "image": "post.jpg", "caption": caption}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Generated date:", date.isoformat())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date")
    args = parser.parse_args()
    generate(args.date)

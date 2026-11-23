"""Create a 1080x1920 Story from today's feed image, preserving the topic."""
import argparse
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--date")
    args=parser.parse_args()
    day=args.date or datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).date().isoformat()
    folder=Path("images")/day
    source=folder/"post.jpg"
    if not source.exists():
        raise SystemExit("Today's feed image missing; refusing to generate an unrelated story")
    with Image.open(source) as original:
        image=Image.new("RGB",(1080,1920),"#101827")
        image.paste(original.convert("RGB"),(0,260))
    draw=ImageDraw.Draw(image)
    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",55)
    small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",36)
    draw.text((75,105),"TODAY'S AI FIND",font=font,fill="#5ce1cf")
    draw.text((75,1720),"MORE PRACTICAL AI TIPS",font=small,fill="white")
    draw.text((75,1790),"@everydayaifinds99",font=small,fill="#5ce1cf")
    image.save(folder/"story.jpg",quality=92)
    print("Story prepared for",day)

if __name__=="__main__":
    main()

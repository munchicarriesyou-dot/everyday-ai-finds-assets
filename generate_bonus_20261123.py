from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
p=Path("images/bonus/2026-11-23-ai-learning")
p.mkdir(parents=True,exist_ok=True)
im=Image.new("RGB",(1080,1350),"#101827")
d=ImageDraw.Draw(im)
def font(n,b=False):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
def line(t,y,n,b=False,c="white"):
    f=font(n,b)
    assert d.textlength(t,font=f)<880
    d.text((100,y),t,font=f,fill=c)
line("EVERYDAY AI FINDS",90,36,False,"#5ce1cf")
line("LEARN ANYTHING",250,76,True)
line("WITH AI",350,76,True)
d.rectangle((100,490,980,498),fill="#5ce1cf")
for i,t in enumerate(["1. Ask for a simple explanation.","2. Request a real-world example.","3. Take a short quiz.","4. Ask AI to explain your mistakes."]):
    line(t,580+i*105,40)
line("Try it with a topic you love.",1090,40,True,"#5ce1cf")
line("@everydayaifinds99",1220,32,False,"#5ce1cf")
im.save(p/"post.jpg",quality=94)

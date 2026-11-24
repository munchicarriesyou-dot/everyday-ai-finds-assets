from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import subprocess, tempfile, math, wave, struct
out=Path("images/reels/2026-11-24.mp4")
out.parent.mkdir(parents=True,exist_ok=True)
scenes=[
("AI IS FOR\nEVERYONE","You don't need to be a tech expert."),
("START SIMPLE","Ask AI to explain something\nyou have always wanted to learn."),
("MAKE IT PERSONAL","Ask for examples from your\nwork, hobbies or everyday life."),
("LEARN AT ANY AGE","Practice with a short quiz.\nAsk follow-up questions."),
("YOUR FIRST STEP","Try one question today.\nFollow for everyday AI tips.")]
with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)
    for i,(title,body) in enumerate(scenes):
        im=Image.new("RGB",(1080,1920),"#101827")
        d=ImageDraw.Draw(im)
        def block(t,y,n,b=False,c="white"):
            while n>20:
                f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans"+("-Bold" if b else "")+".ttf",n)
                box=d.multiline_textbbox((0,0),t,font=f,spacing=24)
                if box[2]-box[0]<=800: break
                n-=2
            d.multiline_text((120-box[0],y-box[1]),t,font=f,spacing=24,fill=c)
        block("EVERYDAY AI FINDS",260,38,c="#5ce1cf")
        d.rectangle((120,360,920,368),fill="#5ce1cf")
        block(title,540,100,True)
        block(body,1000,53,c="#e1ebf5")
        block("@everydayaifinds99",1510,36,c="#5ce1cf")
        for j in range(5):
            d.rounded_rectangle((120+j*164,1630,260+j*164,1644),radius=7,fill="#5ce1cf" if j<=i else "#344256")
        im.save(p/f"{i}.png")
        subprocess.run(["ffmpeg","-loglevel","error","-y","-loop","1","-i",str(p/f"{i}.png"),"-vf","scale=2160:3840,zoompan=z='1+0.00035*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=120:s=1080x1920:fps=30,fade=t=in:st=0:d=0.18,fade=t=out:st=3.82:d=0.18","-t","4","-c:v","libx264","-preset","fast","-pix_fmt","yuv420p",str(p/f"{i}.mp4")],check=True)
    (p/"list.txt").write_text("".join(f"file '{i}.mp4'\n" for i in range(5)))
    with wave.open(str(p/"audio.wav"),"wb") as w:
        w.setparams((1,2,44100,0,"NONE","not compressed"))
        samples=bytearray()
        for k in range(20*44100):
            t=k/44100
            beat=int(t*2)
            freq=[220,261.63,329.63,392,329.63,261.63,293.66,329.63][beat%8]
            env=math.exp(-5*(t%0.5))*min(1,t*5,(20-t)*5)
            samples.extend(struct.pack("<h",int(1800*env*(math.sin(2*math.pi*freq*t)+0.25*math.sin(4*math.pi*freq*t)))))
        w.writeframes(samples)
    subprocess.run(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i",str(p/"list.txt"),"-i",str(p/"audio.wav"),"-c:v","copy","-c:a","aac","-b:a","128k","-movflags","+faststart","-shortest",str(out)],check=True)

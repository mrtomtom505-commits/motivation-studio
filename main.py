import os
import random
import asyncio
import requests
import edge_tts
from fastapi import FastAPI, Request, Form
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

PEXELS_API_KEY = os.getenv("Og5k6ZFpOQA7SqscR7eiV2UMbkhmuvpiB9CaS23P4GzpQCdltn77JMPa")
VOICE = "en-US-AriaNeural"

os.makedirs("videos", exist_ok=True)
os.makedirs("output", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# =========================
# VIRAL TOPIC GENERATOR
# =========================
def generate_topic():
    emotions = ["Pain", "Discipline", "Fear", "Focus", "Consistency", "Hustle"]
    power = ["Will Change Your Life", "Will Make You Unstoppable", "No One Talks About", "That Builds Champions"]
    return f"The {random.choice(emotions)} That {random.choice(power)}"

# =========================
# ULTRA HUMAN SCRIPT
# =========================
def generate_script(topic):
    return f"""
{topic.upper()}.

Nobody wakes up powerful.

They wake up tired.
Doubting.
Questioning.

But the difference between average and elite
is simple.

The elite move anyway.

They move when they don’t feel ready.
They move when it hurts.
They move when motivation disappears.

Because success isn’t built on hype.
It’s built on discipline.

Every silent sacrifice compounds.
Every unseen effort stacks.

One day,
what feels heavy today
will feel like power.

Keep going.
"""

# =========================
# DOWNLOAD PEXELS CLIPS
# =========================
def download_videos(query):
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=3"
    response = requests.get(url, headers=headers)
    data = response.json()

    paths = []

    for i, video in enumerate(data["videos"]):
        video_url = video["video_files"][0]["link"]
        path = f"videos/video{i}.mp4"
        video_data = requests.get(video_url).content
        with open(path, "wb") as f:
            f.write(video_data)
        paths.append(path)

    return paths

# =========================
# TEXT TO SPEECH
# =========================
async def text_to_speech(text, filename):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

# =========================
# CREATE VIDEO WITH MUSIC + SUBTITLE
# =========================
def create_video(topic):
    script = generate_script(topic)
    voice_path = "voice.mp3"

    asyncio.run(text_to_speech(script, voice_path))
    videos = download_videos(topic)

    with open("videos/concat.txt", "w") as f:
        for path in videos:
            f.write(f"file '{os.path.abspath(path)}'\n")

    os.system("ffmpeg -y -f concat -safe 0 -i videos/concat.txt -c copy merged.mp4")

    os.system(f"""
    ffmpeg -y -i merged.mp4 -i {voice_path} -i static/music/bg.mp3 \
    -filter_complex "[2:a]volume=0.2[a2];[1:a][a2]amix=inputs=2:duration=shortest[a]" \
    -map 0:v -map "[a]" \
    -vf "drawtext=text='{topic}':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=h-100" \
    -shortest output/final.mp4
    """)

    return "output/final.mp4"

# =========================
# ROUTES
# =========================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
def generate():
    topic = generate_topic()
    video_path = create_video(topic)
    return FileResponse(video_path, media_type="video/mp4", filename="motivation.mp4")

@app.post("/batch")
def batch():
    for _ in range(5):
        topic = generate_topic()
        create_video(topic)
    return {"status": "5 videos generated"}

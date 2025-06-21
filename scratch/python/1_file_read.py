from pathlib import Path
from markdown import markdown
import json
import re
import os
from PIL import Image
from dotenv import load_dotenv
load_dotenv()

def read_file():
    p = Path("data/f1.txt") # path will be relative to execution path
    print(p.cwd())

    if p.exists():
        with open(p) as f:
            data = f.read()

        print(data)
    else:
        print("file not exist")

# read_file()

def readMD():
    p = Path("data/sample.md")
    if p.exists():
        with open(p) as f:
            content = f.read()
            html = markdown(content)
        print(html)

# readMD()

def subs(m):
    return os.environ.get(m.group(1), m.group(0))


def replace_env(o):
    if isinstance(o, dict):
        return { k: replace_env(v) for k, v in o.items() }
    if isinstance(o, list):
        return [ replace_env(i) for i in o ]
    if isinstance(o, str):
        pattern = re.compile(r"\$\{([^}]+)\}")
        return pattern.sub(subs, o)
    else:
        return o

def load_json():
    p = Path("data/config.json")
    if p.exists():
        with open(p) as f:
            content = json.load(f)
            content_j = replace_env(content)
        print(content_j)

# load_json()

def load_img():
    img = Image.open("data/image.png")
    img.show() 
    resized = img.resize((200, 200))
    resized.save("data/resized.jpg")

# load_img()

def load_image_bytes():
    with open("data/image.png", "rb") as f:
        image_bytes = f.read()
        # print(image_bytes)

# load_image_bytes()
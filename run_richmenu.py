# -*- coding: utf-8 -*-
import os, sys
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'Y3a89mMEU4Q4nKhRM3XOVuBH0rbUjPBgy/iq4++laQvYp63+KcKw3MwSfQXkhTCcecX+jwJlyk16r81EoQ+IRk+sfipDrMYg/TqiHkuNg2EKfahwPc6TgGDTBc0Fa65qEiYuygNbBmrNALRbZvjaIgdB04t89/1O/w1cDnyilFU='

import requests
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

W, H = 2500, 843
COL = W // 3

menu = {
    "size": {"width": W, "height": H},
    "selected": True,
    "name": "South Home Menu",
    "chatBarText": "開啟服務選單",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": COL, "height": H},
            "action": {"type": "postback", "data": "action=booking&appt_type=丈量預約", "label": "丈量預約"}
        },
        {
            "bounds": {"x": COL, "y": 0, "width": COL, "height": H},
            "action": {"type": "postback", "data": "action=store_visit", "label": "門市參觀"}
        },
        {
            "bounds": {"x": COL * 2, "y": 0, "width": COL + 1, "height": H},
            "action": {"type": "postback", "data": "action=color_selection", "label": "線上選色"}
        },
    ]
}

r = requests.post(
    "https://api.line.me/v2/bot/richmenu",
    headers={**HEADERS, "Content-Type": "application/json"},
    json=menu
)
print("Create menu:", r.status_code, r.text[:200])
r.raise_for_status()
menu_id = r.json()["richMenuId"]
print(f"Menu ID: {menu_id}")

img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

colors = ["#3D6B4F", "#5A8A5E", "#7AAD7E"]
labels = ["丈量預約", "門市參觀", "線上選色"]
subs   = ["到府丈量服務", "預約門市參觀", "瀏覽色系目錄"]

try:
    font_title = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 100)
    font_sub   = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 55)
except:
    font_title = ImageFont.load_default()
    font_sub   = font_title

for i, (color, title, sub) in enumerate(zip(colors, labels, subs)):
    x0 = i * COL
    x1 = x0 + COL
    cx = x0 + COL // 2
    draw.rectangle([x0, 0, x1, H], fill=color)
    if i > 0:
        draw.line([x0, 20, x0, H - 20], fill=(255, 255, 255, 60), width=2)
    draw.text((cx, 380), title, fill="white", font=font_title, anchor="mm")
    draw.text((cx, 520), sub, fill="#D4ECD8", font=font_sub, anchor="mm")

img.save("richmenu.png")
print("Image saved")

with open("richmenu.png", "rb") as f:
    r = requests.post(
        f"https://api-data.line.me/v2/bot/richmenu/{menu_id}/content",
        headers={**HEADERS, "Content-Type": "image/png"},
        data=f
    )
print("Upload:", r.status_code)

r = requests.post(
    f"https://api.line.me/v2/bot/user/all/richmenu/{menu_id}",
    headers=HEADERS
)
print("Set default:", r.status_code)
print("Done!", menu_id)

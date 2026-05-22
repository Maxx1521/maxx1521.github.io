# -*- coding: utf-8 -*-
import os, sys
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'Y3a89mMEU4Q4nKhRM3XOVuBH0rbUjPBgy/iq4++laQvYp63+KcKw3MwSfQXkhTCcecX+jwJlyk16r81EoQ+IRk+sfipDrMYg/TqiHkuNg2EKfahwPc6TgGDTBc0Fa65qEiYuygNbBmrNALRbZvjaIgdB04t89/1O/w1cDnyilFU='

import requests
from PIL import Image, ImageDraw, ImageFont

TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

W, H = 2500, 1686
TOP_H = 1050   # 上排三格高度
BOT_H = H - TOP_H  # 下排一格高度
COL = W // 3

menu = {
    "size": {"width": W, "height": H},
    "selected": True,
    "name": "South Home Menu v2",
    "chatBarText": "開啟服務選單",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": COL, "height": TOP_H},
            "action": {"type": "message", "text": "估價", "label": "免費估價"}
        },
        {
            "bounds": {"x": COL, "y": 0, "width": COL, "height": TOP_H},
            "action": {"type": "message", "text": "案例", "label": "施工案例"}
        },
        {
            "bounds": {"x": COL * 2, "y": 0, "width": COL + 1, "height": TOP_H},
            "action": {"type": "message", "text": "材質", "label": "材質介紹"}
        },
        {
            "bounds": {"x": 0, "y": TOP_H, "width": W, "height": BOT_H},
            "action": {"type": "postback", "data": "action=booking&appt_type=丈量預約", "label": "聯絡我們/預約丈量"}
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

try:
    font_main = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 110)
    font_sub  = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 60)
    font_bot  = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 90)
    font_bot_sub = ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 55)
except:
    font_main = ImageFont.load_default()
    font_sub  = font_main
    font_bot  = font_main
    font_bot_sub = font_main

# 上排三格
top_colors = ["#3D6B4F", "#5A8A5E", "#7AAD7E"]
top_labels = ["📐 免費估價", "📷 施工案例", "🪵 材質介紹"]
top_subs   = ["免費到府丈量報價", "近期工程實例", "超耐磨/海島/實木"]

for i, (color, title, sub) in enumerate(zip(top_colors, top_labels, top_subs)):
    x0 = i * COL
    x1 = x0 + COL
    cx = x0 + COL // 2
    cy = TOP_H // 2
    draw.rectangle([x0, 0, x1, TOP_H], fill=color)
    if i > 0:
        draw.line([x0, 30, x0, TOP_H - 30], fill=(255, 255, 255, 60), width=2)
    draw.text((cx, cy - 60), title, fill="white", font=font_main, anchor="mm")
    draw.text((cx, cy + 80), sub, fill="#D4ECD8", font=font_sub, anchor="mm")

# 下排全寬
draw.rectangle([0, TOP_H, W, H], fill="#2A4F38")
draw.line([0, TOP_H, W, TOP_H], fill=(255, 255, 255, 80), width=3)
bot_cy = TOP_H + BOT_H // 2
draw.text((W // 2, bot_cy - 45), "💬 聯絡我們 / 預約丈量", fill="white", font=font_bot, anchor="mm")
draw.text((W // 2, bot_cy + 65), "點此預約免費到府丈量", fill="#A8CFAD", font=font_bot_sub, anchor="mm")

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

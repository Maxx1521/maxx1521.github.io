import os
from datetime import datetime, timedelta
from linebot.v3.messaging import (
    FlexMessage, FlexContainer, TextMessage,
    QuickReply, QuickReplyItem, PostbackAction,
    ApiClient, Configuration, MessagingApi, PushMessageRequest
)
from supabase import create_client

_supabase = None

def get_supabase():
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        _supabase = create_client(url, key)
    return _supabase


def push_owner_notification(date, time, product):
    owner_id = os.environ.get("OWNER_LINE_USER_ID")
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not owner_id or not token:
        return
    try:
        product_text = f"\n📦 商品：{product}" if product else ""
        msg = f"📬 新預約通知\n\n📅 日期：{date}\n🕐 時間：{time}{product_text}\n\n請至後台確認客戶資訊。"
        config = Configuration(access_token=token)
        with ApiClient(config) as client:
            MessagingApi(client).push_message(
                PushMessageRequest(to=owner_id, messages=[TextMessage(text=msg)])
            )
    except Exception as e:
        print(f"[push notify error] {e}")


def start_booking(product=None):
    quick_items = []
    for i in range(1, 8):
        date = datetime.now() + timedelta(days=i)
        label = date.strftime("%m/%d (%a)")
        data = f"action=select_date&date={date.strftime('%Y-%m-%d')}"
        if product:
            data += f"&product={product}"
        quick_items.append(
            QuickReplyItem(action=PostbackAction(label=label, data=data))
        )

    return TextMessage(
        text="📅 預約到府丈量\n\n請選擇希望的日期：",
        quick_reply=QuickReply(items=quick_items)
    )


def select_time(date, product=None):
    times = ["10:00", "14:00", "16:00"]
    quick_items = []
    for t in times:
        data = f"action=select_time&date={date}&time={t}"
        if product:
            data += f"&product={product}"
        quick_items.append(
            QuickReplyItem(action=PostbackAction(label=t, data=data))
        )

    return TextMessage(
        text=f"📅 已選擇 {date}\n\n請選擇希望的時段：",
        quick_reply=QuickReply(items=quick_items)
    )


def confirm_booking(user_id, date, time, product=None):
    record = {
        "user_id": user_id,
        "date": date,
        "time": time,
        "product": product,
        "status": "pending",
    }
    try:
        get_supabase().table("bookings").insert(record).execute()
    except Exception as e:
        print(f"[Supabase error] {e}")

    push_owner_notification(date, time, product)

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "✅ 預約確認", "weight": "bold", "size": "xl", "color": "#5C8D5E"},
                {"type": "separator", "margin": "md"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box", "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "日期", "size": "sm", "color": "#888888", "flex": 2},
                                {"type": "text", "text": date, "size": "sm", "flex": 5},
                            ]
                        },
                        {
                            "type": "box", "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "時間", "size": "sm", "color": "#888888", "flex": 2},
                                {"type": "text", "text": time, "size": "sm", "flex": 5},
                            ]
                        },
                    ] + ([{
                        "type": "box", "layout": "horizontal",
                        "contents": [
                            {"type": "text", "text": "商品", "size": "sm", "color": "#888888", "flex": 2},
                            {"type": "text", "text": product, "size": "sm", "flex": 5, "wrap": True},
                        ]
                    }] if product else [])
                },
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": "我們將於預約前一天與您確認地址及聯絡方式，謝謝！",
                    "size": "xs", "color": "#888888", "wrap": True, "margin": "md"
                },
            ],
        },
    }

    return FlexMessage(
        alt_text=f"預約確認 {date} {time}",
        contents=FlexContainer.from_dict(bubble)
    )

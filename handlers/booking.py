import os
from datetime import datetime, timedelta, timezone
from linebot.v3.messaging import (
    FlexMessage, FlexContainer, TextMessage,
    QuickReply, QuickReplyItem, PostbackAction,
    ApiClient, Configuration, MessagingApi, PushMessageRequest
)
from supabase import create_client

_supabase = None

WAITING_NAME    = "waiting_name"
WAITING_PHONE   = "waiting_phone"
WAITING_ADDRESS = "waiting_address"
WAITING_CONFIRM = "waiting_confirm"


def get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.environ.get("SUPABASE_URL"),
            os.environ.get("SUPABASE_KEY")
        )
    return _supabase


# ── 對話狀態管理 ────────────────────────────────

def get_session(user_id):
    try:
        r = get_supabase().table("user_sessions").select("*").eq("user_id", user_id).maybe_single().execute()
        return r.data
    except Exception as e:
        print(f"[session get error] {e}")
        return None


def _upsert_session(data):
    try:
        payload = {**data, "updated_at": datetime.now(timezone.utc).isoformat()}
        get_supabase().table("user_sessions").upsert(payload).execute()
    except Exception as e:
        print(f"[session upsert error] {e}")


def _delete_session(user_id):
    try:
        get_supabase().table("user_sessions").delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"[session delete error] {e}")


# ── 預約流程 ─────────────────────────────────────

_WEEKDAYS = ["(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "(日)"]


def start_booking(product=None, appt_type="丈量預約"):
    quick_items = []
    for i in range(1, 8):
        date = datetime.now() + timedelta(days=i)
        label = date.strftime("%m/%d") + _WEEKDAYS[date.weekday()]
        data = f"action=select_date&date={date.strftime('%Y-%m-%d')}&appt_type={appt_type}"
        if product:
            data += f"&product={product}"
        quick_items.append(
            QuickReplyItem(action=PostbackAction(label=label, data=data))
        )
    icon = "📅" if appt_type == "丈量預約" else "🏠"
    return TextMessage(
        text=f"{icon} {appt_type}\n\n請選擇希望的日期：",
        quick_reply=QuickReply(items=quick_items)
    )


def select_time(date, product=None, appt_type="丈量預約"):
    times = ["10:00", "14:00", "16:00"]
    quick_items = []
    for t in times:
        data = f"action=select_time&date={date}&time={t}&appt_type={appt_type}"
        if product:
            data += f"&product={product}"
        quick_items.append(
            QuickReplyItem(action=PostbackAction(label=t, data=data))
        )
    return TextMessage(
        text=f"📅 已選擇 {date}\n\n請選擇希望的時段：",
        quick_reply=QuickReply(items=quick_items)
    )


def ask_for_name(user_id, appt_type, date, time, product=None):
    _upsert_session({
        "user_id": user_id,
        "state": WAITING_NAME,
        "appt_type": appt_type,
        "date": date,
        "time": time,
        "product": product,
    })
    return TextMessage(text="好的！請問您的姓名？")


def handle_name_input(user_id, name, session):
    _upsert_session({**session, "state": WAITING_PHONE, "name": name})
    return TextMessage(text=f"謝謝 {name}！\n\n📱 請問您的聯絡電話？")


def handle_phone_input(user_id, phone, session):
    _upsert_session({**session, "state": WAITING_ADDRESS, "phone": phone})
    return TextMessage(text="📍 請問您的地址？")


def handle_address_input(user_id, address, session):
    updated = {**session, "state": WAITING_CONFIRM, "address": address}
    _upsert_session(updated)
    return _review_card(updated)


def handle_confirm(user_id, session):
    """客戶確認，正式寫入資料庫"""
    record = {
        "user_id":   user_id,
        "appt_type": session["appt_type"],
        "date":      session["date"],
        "time":      session["time"],
        "product":   session.get("product"),
        "name":      session.get("name", ""),
        "phone":     session.get("phone", ""),
        "address":   session.get("address", ""),
        "status":    "pending",
    }
    try:
        get_supabase().table("bookings").insert(record).execute()
    except Exception as e:
        print(f"[Supabase error] {e}")

    _delete_session(user_id)
    push_owner_notification(
        session["appt_type"], session["date"], session["time"],
        session.get("name",""), session.get("phone",""),
        session.get("address",""), session.get("product")
    )
    return _success_card(session)


def handle_edit_field(user_id, field, session):
    """客戶要修改某一欄位"""
    prompts = {
        "name":    (WAITING_NAME,    "請重新輸入您的姓名："),
        "phone":   (WAITING_PHONE,   "請重新輸入您的電話："),
        "address": (WAITING_ADDRESS, "請重新輸入您的地址："),
    }
    state, prompt = prompts.get(field, (WAITING_NAME, "請重新輸入您的姓名："))
    _upsert_session({**session, "state": state})
    return TextMessage(text=prompt)


# ── 卡片 ─────────────────────────────────────────

def _review_card(session):
    """讓客戶確認填寫內容的摘要卡片"""
    appt_type = session["appt_type"]
    icon = "📅" if appt_type == "丈量預約" else "🏠"

    rows = [
        ("類型", f"{icon} {appt_type}"),
        ("日期", session["date"]),
        ("時間", session["time"]),
        ("姓名", session.get("name", "")),
        ("電話", session.get("phone", "")),
        ("地址", session.get("address", "")),
    ]
    if session.get("product"):
        rows.append(("商品", session["product"]))

    contents = []
    for label, value in rows:
        contents.append({
            "type": "box", "layout": "horizontal",
            "contents": [
                {"type": "text", "text": label, "size": "sm", "color": "#888888", "flex": 2},
                {"type": "text", "text": value or "—", "size": "sm", "flex": 5, "wrap": True},
            ]
        })

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": "📋 請確認您的預約資料",
                 "weight": "bold", "size": "lg", "color": "#5C8D5E"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md",
                 "spacing": "sm", "contents": contents},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": "資料有誤？請點下方快捷鍵修改。",
                 "size": "xs", "color": "#aaaaaa", "wrap": True, "margin": "md"},
            ],
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{
                "type": "button",
                "action": {"type": "postback", "label": "✅ 確認送出",
                           "data": "action=confirm_booking"},
                "style": "primary", "color": "#5C8D5E",
            }],
        },
    }

    quick_reply = QuickReply(items=[
        QuickReplyItem(action=PostbackAction(label="✏️ 改姓名", data="action=edit_field&field=name")),
        QuickReplyItem(action=PostbackAction(label="✏️ 改電話", data="action=edit_field&field=phone")),
        QuickReplyItem(action=PostbackAction(label="✏️ 改地址", data="action=edit_field&field=address")),
    ])

    return FlexMessage(
        alt_text="請確認您的預約資料",
        contents=FlexContainer.from_dict(bubble),
        quick_reply=quick_reply
    )


def _success_card(session):
    appt_type = session["appt_type"]
    icon = "📅" if appt_type == "丈量預約" else "🏠"
    rows = [
        ("類型", f"{icon} {appt_type}"),
        ("姓名", session.get("name", "")),
        ("日期", session["date"]),
        ("時間", session["time"]),
    ]
    contents = []
    for label, value in rows:
        contents.append({
            "type": "box", "layout": "horizontal",
            "contents": [
                {"type": "text", "text": label, "size": "sm", "color": "#888888", "flex": 2},
                {"type": "text", "text": value or "—", "size": "sm", "flex": 5},
            ]
        })

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": "✅ 預約申請已收到",
                 "weight": "bold", "size": "xl", "color": "#5C8D5E"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md",
                 "spacing": "sm", "contents": contents},
                {"type": "separator", "margin": "md"},
                {"type": "text",
                 "text": "我們將請專人與您確認時間，謝謝！",
                 "size": "xs", "color": "#888888", "wrap": True, "margin": "md"},
            ],
        },
    }
    return FlexMessage(
        alt_text="預約申請已收到",
        contents=FlexContainer.from_dict(bubble)
    )


# ── 推播通知 ─────────────────────────────────────

def push_success_to_customer(user_id, session):
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        return
    try:
        config = Configuration(access_token=token)
        with ApiClient(config) as client:
            MessagingApi(client).push_message(
                PushMessageRequest(to=user_id, messages=[_success_card(session)])
            )
    except Exception as e:
        print(f"[push customer error] {e}")


def push_owner_notification(appt_type, date, time, name, phone, address, product):
    owner_id = os.environ.get("OWNER_LINE_USER_ID")
    token    = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not owner_id or not token:
        return
    try:
        product_text = f"\n📦 商品：{product}" if product else ""
        msg = (
            f"📬 新預約申請\n\n"
            f"🏷 類型：{appt_type}\n"
            f"👤 姓名：{name}\n"
            f"📱 電話：{phone}\n"
            f"📍 地址：{address}\n"
            f"📅 日期：{date}\n"
            f"🕐 時間：{time}{product_text}"
        )
        config = Configuration(access_token=token)
        with ApiClient(config) as client:
            MessagingApi(client).push_message(
                PushMessageRequest(to=owner_id, messages=[TextMessage(text=msg)])
            )
    except Exception as e:
        print(f"[push notify error] {e}")

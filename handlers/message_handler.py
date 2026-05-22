import os
from linebot.v3.messaging import (
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer,
    QuickReply, QuickReplyItem, MessageAction, PostbackAction, URIAction
)
from handlers.catalog import get_category_flex
from handlers.booking import (
    start_booking, get_session,
    handle_name_input, handle_phone_input, handle_address_input,
    WAITING_NAME, WAITING_PHONE, WAITING_ADDRESS, WAITING_CONFIRM
)


MENU_KEYWORDS        = ["選單", "menu", "Menu", "MENU", "你好", "hi", "Hi", "HI", "hello", "Hello"]
CATALOG_KEYWORDS     = ["產品", "目錄", "地板", "看地板", "產品目錄"]
BOOKING_KEYWORDS     = ["預約", "丈量", "到府", "預約丈量", "丈量預約"]
STORE_VISIT_KEYWORDS = ["門市", "門市參觀", "參觀", "來店"]
COLOR_KEYWORDS       = ["選色", "線上選色", "色卡", "顏色"]


def handle_text_message(event, line_bot_api):
    text    = event.message.text.strip()
    user_id = event.source.user_id

    # 優先檢查對話狀態（正在填寫資料中）
    session = get_session(user_id)
    if session:
        state = session.get("state")
        if state == WAITING_NAME:
            reply = handle_name_input(user_id, text, session)
        elif state == WAITING_PHONE:
            reply = handle_phone_input(user_id, text, session)
        elif state == WAITING_ADDRESS:
            reply = handle_address_input(user_id, text, session)
        elif state == WAITING_CONFIRM:
            reply = TextMessage(text="請點選「✅ 確認送出」送出預約，或點快捷鍵修改資料。")
        else:
            reply = TextMessage(text="請輸入「選單」查看服務項目。")
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
        )
        return

    # 一般關鍵字處理
    if text.lower() == "我的id":
        reply = TextMessage(text=f"你的 LINE user ID：\n{user_id}")
    elif any(k in text for k in MENU_KEYWORDS):
        reply = _main_menu()
    elif any(k in text for k in CATALOG_KEYWORDS):
        reply = get_category_flex()
    elif any(k in text for k in BOOKING_KEYWORDS):
        reply = start_booking(appt_type="丈量預約")
    elif any(k in text for k in STORE_VISIT_KEYWORDS):
        reply = start_booking(appt_type="門市參觀")
    elif any(k in text for k in COLOR_KEYWORDS):
        reply = _color_selection_message()
    else:
        reply = TextMessage(text="您好！請點選下方選單，或輸入「選單」查看服務項目 🌿")

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
    )


def _color_selection_message():
    color_url = os.environ.get("COLOR_SELECTION_URL", "https://notion.so")
    bubble = {
        "type": "bubble",
        "hero": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": "🎨", "size": "5xl", "align": "center", "margin": "xl"},
                {"type": "text", "text": "線上選色", "weight": "bold", "size": "xl",
                 "align": "center", "color": "#5C8D5E", "margin": "md"},
                {"type": "text", "text": "瀏覽我們精選的地板色系\n找到最適合您家的風格",
                 "size": "sm", "align": "center", "color": "#888888", "wrap": True, "margin": "sm"},
            ],
            "paddingAll": "20px",
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{
                "type": "button",
                "action": {"type": "uri", "label": "前往線上選色 →", "uri": color_url},
                "style": "primary", "color": "#5C8D5E",
            }],
        },
    }
    return FlexMessage(alt_text="線上選色", contents=FlexContainer.from_dict(bubble))


def _main_menu():
    return TextMessage(
        text="歡迎來到南島家居 South Home 🌿\n\n請選擇服務：",
        quick_reply=QuickReply(items=[
            QuickReplyItem(action=PostbackAction(label="📅 丈量預約", data="action=booking&appt_type=丈量預約")),
            QuickReplyItem(action=PostbackAction(label="🏠 門市參觀", data="action=store_visit")),
            QuickReplyItem(action=PostbackAction(label="🎨 線上選色", data="action=color_selection")),
            QuickReplyItem(action=PostbackAction(label="🪵 產品目錄", data="action=catalog")),
        ])
    )

from linebot.v3.messaging import (
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer,
    QuickReply, QuickReplyItem, MessageAction, PostbackAction
)
from handlers.catalog import get_category_flex
from handlers.booking import start_booking


MENU_KEYWORDS = ["選單", "menu", "Menu", "MENU", "你好", "hi", "Hi", "HI", "hello", "Hello"]
CATALOG_KEYWORDS = ["產品", "目錄", "地板", "看地板", "產品目錄"]
BOOKING_KEYWORDS = ["預約", "丈量", "到府", "預約丈量"]


def handle_text_message(event, line_bot_api):
    text = event.message.text.strip()

    if text.lower() == "我的id":
        reply = TextMessage(text=f"你的 LINE user ID：\n{event.source.user_id}")
    elif any(k in text for k in MENU_KEYWORDS):
        reply = _main_menu()
    elif any(k in text for k in CATALOG_KEYWORDS):
        reply = get_category_flex()
    elif any(k in text for k in BOOKING_KEYWORDS):
        reply = start_booking()
    else:
        reply = TextMessage(text="您好！請點選下方選單，或輸入「選單」查看服務項目 🌿")

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
    )


def _main_menu():
    return TextMessage(
        text="歡迎來到南島家居 South Home 🌿\n\n請選擇服務：",
        quick_reply=QuickReply(items=[
            QuickReplyItem(action=PostbackAction(
                label="🪵 產品目錄", data="action=catalog"
            )),
            QuickReplyItem(action=PostbackAction(
                label="📅 預約丈量", data="action=booking"
            )),
            QuickReplyItem(action=MessageAction(
                label="📞 聯絡我們", text="請問聯絡方式？"
            )),
        ])
    )

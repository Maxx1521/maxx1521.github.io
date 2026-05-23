import os
from linebot.v3.messaging import (
    ReplyMessageRequest, TextMessage, FlexMessage, FlexContainer,
    QuickReply, QuickReplyItem, MessageAction, PostbackAction, URIAction
)
from handlers.catalog import get_category_flex
from handlers.booking import (
    start_booking, get_session, select_time, _parse_date_text, _is_bookable_date,
    handle_name_input, handle_phone_input, handle_address_input,
    ask_for_date, handle_date_input,
    WAITING_DATE, WAITING_NAME, WAITING_PHONE, WAITING_ADDRESS, WAITING_CONFIRM
)
from handlers.location import (
    start_location_inquiry, handle_area_input, WAITING_AREA
)


MENU_KEYWORDS        = ["選單", "menu", "Menu", "MENU", "你好", "hi", "Hi", "HI", "hello", "Hello"]
CATALOG_KEYWORDS     = ["產品", "目錄", "看地板", "產品目錄"]
BOOKING_KEYWORDS     = ["預約", "丈量", "到府", "預約丈量", "丈量預約"]
STORE_VISIT_KEYWORDS = ["門市參觀", "參觀", "來店"]
LOCATION_KEYWORDS    = ["門市在哪", "門市地址", "你們在哪", "門市位置", "門市地點", "地址在哪", "地址在哪裡", "在哪裡", "門市"]
COLOR_KEYWORDS       = ["選色", "線上選色", "色卡", "顏色"]
OTHER_DATE_KEYWORDS  = ["還有其他時間", "其他時間", "其他日期", "換個時間", "可以換時間", "其他時段", "沒有其他", "其他時間可以選嗎"]
QUOTE_KEYWORDS       = ["估價", "報價", "多少錢", "費用", "收費"]
PORTFOLIO_KEYWORDS   = ["案例", "作品", "照片", "實例", "實拍", "before", "after", "前後"]
MATERIAL_KEYWORDS    = ["材質", "地板種類", "哪種好", "超耐磨", "實木", "海島型", "磁磚"]
CARE_KEYWORDS        = ["保養", "清潔", "維護", "髒了"]


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
        elif state == WAITING_DATE:
            reply = handle_date_input(user_id, text, session)
        elif state == WAITING_AREA:
            reply = handle_area_input(user_id, text)
        else:
            reply = TextMessage(text="請輸入「選單」查看服務項目。")
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
        )
        return

    # 直接輸入日期 → 跳時段選擇
    date_str = _parse_date_text(text)
    if date_str:
        if not _is_bookable_date(date_str):
            reply = TextMessage(text="⚠️ 無法預約該日期，請選擇明天以後的時段。")
        else:
            reply = select_time(date_str)
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
    elif any(k in text for k in OTHER_DATE_KEYWORDS):
        reply = ask_for_date(user_id)
    elif any(k in text for k in LOCATION_KEYWORDS):
        reply = start_location_inquiry(user_id)
    elif any(k in text for k in STORE_VISIT_KEYWORDS):
        reply = start_booking(appt_type="門市參觀")
    elif any(k in text for k in COLOR_KEYWORDS):
        reply = _color_selection_message()
    elif any(k in text for k in QUOTE_KEYWORDS):
        reply = _quote_message()
    elif any(k in text for k in PORTFOLIO_KEYWORDS):
        reply = _portfolio_message()
    elif any(k in text for k in MATERIAL_KEYWORDS):
        reply = _material_message()
    elif any(k in text for k in CARE_KEYWORDS):
        reply = _care_message()
    else:
        reply = _fallback_menu(text)

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
    )


def _fallback_menu(text=""):
    DATE_WORDS = ["6月", "7月", "8月", "9月", "10月", "11月", "12月", "下個月", "下下個月", "月份", "幾號", "哪天", "什麼時候"]
    if any(w in text for w in DATE_WORDS):
        msg = "目前預約系統開放未來 15 天的時段，請直接點選日期選擇 📅"
    else:
        msg = "您好！請點選下方選單查看服務項目 🌿"
    return TextMessage(
        text=msg,
        quick_reply=QuickReply(items=[
            QuickReplyItem(action=PostbackAction(label="📅 丈量預約", data="action=booking&appt_type=丈量預約")),
            QuickReplyItem(action=PostbackAction(label="🏠 門市參觀", data="action=store_visit")),
            QuickReplyItem(action=PostbackAction(label="🏠 門市地址", data="action=location_inquiry")),
            QuickReplyItem(action=PostbackAction(label="🪵 產品目錄", data="action=catalog")),
        ])
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


def _quote_message():
    return TextMessage(
        text=(
            "感謝您的詢問！📐\n\n"
            "南島家居提供【免費到府丈量 + 快速報價】服務。\n\n"
            "請提供以下資訊，我們將盡快回覆：\n\n"
            "1️⃣ 施工地點（縣市區域）\n"
            "2️⃣ 空間坪數（大約幾坪）\n"
            "3️⃣ 地板目前狀況（舊地板／水泥地／其他）\n"
            "4️⃣ 預計施工時間（越快越好／某月份）\n\n"
            "歡迎直接回覆此訊息，或來電洽詢 🙌"
        )
    )


def _portfolio_message():
    return TextMessage(
        text=(
            "這是我們近期的施工案例 📷\n\n"
            "從選材到施工，全程由我們負責品質。\n\n"
            "✅ 客廳｜臥室｜商業空間 都有施工經驗\n"
            "✅ 超耐磨、海島型、實木 各類材質均可施作\n\n"
            "想看更多案例，歡迎追蹤我們的 IG 👇\n"
            "@south_woodenn\n\n"
            "有看到喜歡的風格，輸入「估價」預約免費丈量 😊"
        )
    )


def _material_message():
    return TextMessage(
        text=(
            "台灣常見地板材質比較 🪵\n\n"
            "【超耐磨木地板】\n"
            "✅ 耐刮、好保養、價格親民\n"
            "✅ 適合：有小孩/寵物的家庭\n"
            "⚠️ 腳感較硬，非天然木材\n\n"
            "【海島型實木地板】\n"
            "✅ 天然木紋、腳感溫潤\n"
            "✅ 適合：臥室、書房\n"
            "⚠️ 台灣濕氣較重需注意保養\n\n"
            "【實木地板】\n"
            "✅ 最天然、質感最佳\n"
            "✅ 適合：乾燥空間、高預算\n"
            "⚠️ 價格較高，需定期保養\n\n"
            "不確定哪種適合你的空間？\n"
            "輸入「估價」預約免費丈量，現場評估最準確 📐"
        )
    )


def _care_message():
    return TextMessage(
        text=(
            "木地板保養 3 招，讓地板多撐好幾年 🧹\n\n"
            "【日常清潔】\n"
            "✅ 用擰乾的拖把，避免積水\n"
            "✅ 不要用鋼刷或研磨清潔劑\n"
            "✅ 灰塵先吸乾，再濕拖\n\n"
            "【防刮保護】\n"
            "✅ 家具腳加貼軟墊貼片\n"
            "✅ 避免高跟鞋直接踩踏\n"
            "✅ 寵物爪子定期修剪\n\n"
            "【長期維護】\n"
            "✅ 每年塗一次木地板蠟（超耐磨不需要）\n"
            "✅ 保持室內通風，避免長期潮濕\n"
            "✅ 局部損傷可局部補修，不用整片換\n\n"
            "地板有損傷或疑問？\n"
            "輸入「估價」，我們到府評估完全免費 😊"
        )
    )

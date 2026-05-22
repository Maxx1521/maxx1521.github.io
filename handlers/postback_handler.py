from urllib.parse import parse_qs
from linebot.v3.messaging import ReplyMessageRequest, TextMessage
from handlers.catalog import get_category_flex, get_products_flex
from handlers.booking import (
    start_booking, select_time, ask_for_name,
    handle_confirm, handle_edit_field, get_session
)


def handle_postback(event, line_bot_api):
    data = parse_qs(event.postback.data)
    action = data.get("action", [""])[0]
    user_id = event.source.user_id
    appt_type = data.get("appt_type", ["丈量預約"])[0]

    if action == "catalog":
        reply = get_category_flex()

    elif action == "view_category":
        category = data.get("category", [""])[0]
        reply = get_products_flex(category)

    elif action == "booking":
        product = data.get("product", [None])[0]
        reply = start_booking(product, appt_type)

    elif action == "store_visit":
        reply = start_booking(appt_type="門市參觀")

    elif action == "color_selection":
        from handlers.message_handler import _color_selection_message
        reply = _color_selection_message()

    elif action == "select_date":
        date = data.get("date", [""])[0]
        product = data.get("product", [None])[0]
        reply = select_time(date, product, appt_type)

    elif action == "select_time":
        date = data.get("date", [""])[0]
        time = data.get("time", [""])[0]
        product = data.get("product", [None])[0]
        reply = ask_for_name(user_id, appt_type, date, time, product)

    elif action == "confirm_booking":
        session = get_session(user_id)
        if session:
            reply = handle_confirm(user_id, session)
        else:
            reply = TextMessage(text="找不到您的預約資料，請重新開始。")

    elif action == "edit_field":
        field = data.get("field", ["name"])[0]
        session = get_session(user_id)
        if session:
            reply = handle_edit_field(user_id, field, session)
        else:
            reply = TextMessage(text="找不到您的預約資料，請重新開始。")

    else:
        reply = TextMessage(text="請輸入「選單」查看服務項目。")

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
    )

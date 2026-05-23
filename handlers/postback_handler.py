from urllib.parse import parse_qs
from linebot.v3.messaging import (
    ReplyMessageRequest, TextMessage, QuickReply, QuickReplyItem, PostbackAction
)
from handlers.catalog import get_category_flex, get_products_flex, get_brand_products_flex, get_product_colors
from handlers.booking import (
    start_booking, select_time, ask_for_name,
    handle_confirm, handle_edit_field, get_session, _delete_session,
    push_appointment_confirmation, _review_card, _upsert_session
)
from handlers.location import start_location_inquiry


def handle_postback(event, line_bot_api):
    data = parse_qs(event.postback.data)
    action = data.get("action", [""])[0]
    user_id = event.source.user_id
    appt_type = data.get("appt_type", ["丈量預約"])[0]

    store = data.get("store", [None])[0]

    if action == "catalog":
        reply = get_category_flex()

    elif action == "view_category":
        category = data.get("category", [""])[0]
        reply = get_products_flex(category)

    elif action == "view_brand":
        brand = data.get("brand", [""])[0]
        reply = get_brand_products_flex(brand)

    elif action == "view_colors":
        brand = data.get("brand", [""])[0]
        product = data.get("product", [""])[0]
        reply = get_product_colors(brand, product)

    elif action == "booking":
        product = data.get("product", [None])[0]
        reply = start_booking(product, appt_type)

    elif action == "store_visit":
        if store:
            reply = start_booking(appt_type="門市參觀", store=store, user_id=user_id)
        else:
            reply = TextMessage(
                text="請問您想預約哪間門市？",
                quick_reply=QuickReply(items=[
                    QuickReplyItem(action=PostbackAction(label="左營南屏店", data="action=store_visit&store=左營店", display_text="左營南屏店")),
                    QuickReplyItem(action=PostbackAction(label="三民大昌店", data="action=store_visit&store=三民店", display_text="三民大昌店")),
                    QuickReplyItem(action=PostbackAction(label="苓雅青年店", data="action=store_visit&store=苓雅店", display_text="苓雅青年店")),
                ])
            )

    elif action == "color_selection":
        from handlers.message_handler import _color_selection_message
        reply = _color_selection_message()

    elif action == "select_date":
        date = data.get("date", [""])[0]
        product = data.get("product", [None])[0]
        _delete_session(user_id)
        reply = select_time(date, product, appt_type, store)

    elif action == "select_time":
        date = data.get("date", [""])[0]
        time = data.get("time", [""])[0]
        product = data.get("product", [None])[0]
        if appt_type == "門市參觀" and store:
            product = store
        reply = ask_for_name(user_id, appt_type, date, time, product, line_bot_api)

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

    elif action == "location_inquiry":
        reply = start_location_inquiry(user_id)

    elif action == "update_store":
        session = get_session(user_id)
        if session and store:
            updated = {**session, "product": store}
            _upsert_session(updated)
            reply = _review_card(updated)
        else:
            reply = TextMessage(text="找不到您的預約資料，請重新開始。")

    elif action == "confirm_appointment":
        customer_id = data.get("customer_id", [""])[0]
        appt_date   = data.get("date", [""])[0]
        appt_time   = data.get("time", [""])[0]
        appt_store  = data.get("store", [None])[0]
        push_appointment_confirmation(customer_id, appt_date, appt_time, appt_store)
        reply = TextMessage(text="✅ 已通知客人時間確認！")

    else:
        reply = TextMessage(text="請輸入「選單」查看服務項目。")

    line_bot_api.reply_message(
        ReplyMessageRequest(reply_token=event.reply_token, messages=[reply])
    )

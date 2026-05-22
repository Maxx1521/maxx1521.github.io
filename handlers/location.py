from linebot.v3.messaging import TextMessage, QuickReply, QuickReplyItem, PostbackAction
from handlers.booking import _upsert_session, _delete_session

WAITING_AREA = "waiting_area"

# 三間門市資料
STORES = [
    {
        "name": "左營店",
        "address": "高雄市左營區南屏路206號",
        "districts": [
            "左營", "楠梓", "岡山", "橋頭", "梓官", "永安", "彌陀",
            "湖內", "茄萣", "燕巢", "田寮", "阿蓮", "路竹", "旗山",
            "內門", "美濃", "六龜", "杉林", "甲仙", "茂林", "桃源", "那瑪夏",
            "仁武",
        ],
    },
    {
        "name": "三民店",
        "address": "高雄市三民區大昌一路362號",
        "districts": ["三民", "鼓山", "鹽埕", "前金", "新興"],
    },
    {
        "name": "苓雅店",
        "address": "高雄市苓雅區青年一路109-2號",
        "districts": ["苓雅", "前鎮", "小港", "鳳山", "林園", "大寮", "大樹", "旗津"],
    },
]

APPOINTMENT_NOTE = "⚠️ 門市需提前預約，歡迎透過以下選項安排時間。"


def start_location_inquiry(user_id):
    _upsert_session({"user_id": user_id, "state": WAITING_AREA})
    return TextMessage(text="請問您在高雄哪個區域呢？\n我們將推薦離您最近的門市 🏠\n\n（例如：左營、三民、鳳山…）")


def handle_area_input(user_id, area):
    _delete_session(user_id)

    matched = _find_nearest_store(area)

    if matched:
        return TextMessage(
            text=f"🏠 推薦您前往 {matched['name']}\n\n"
                 f"📍 地址：{matched['address']}\n\n"
                 f"{APPOINTMENT_NOTE}",
            quick_reply=QuickReply(items=[
                QuickReplyItem(action=PostbackAction(
                    label="📅 預約門市參觀",
                    data=f"action=store_visit&store={matched['name']}"
                )),
            ])
        )
    else:
        # 無法匹配 or 非高雄 → 列出全部三間
        store_list = "\n\n".join(
            f"🏬 {s['name']}\n📍 {s['address']}" for s in STORES
        )
        return TextMessage(
            text=f"我們目前在高雄設有三間門市：\n\n{store_list}\n\n{APPOINTMENT_NOTE}",
            quick_reply=QuickReply(items=[
                QuickReplyItem(action=PostbackAction(
                    label="📅 預約門市參觀",
                    data="action=store_visit"
                )),
            ])
        )


def _find_nearest_store(area):
    for store in STORES:
        for district in store["districts"]:
            if district in area:
                return store
    return None

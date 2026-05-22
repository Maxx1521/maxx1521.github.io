# -*- coding: utf-8 -*-
import sys, json, time, hmac, hashlib, base64, uuid, requests

sys.stdout.reconfigure(encoding='utf-8')

WEBHOOK_URL    = "https://south-home-linebot.onrender.com/webhook"
CHANNEL_SECRET = "3b8441d65259b2874de4af6daa09e098"
TEST_USER_ID   = "U_test_flow_001"


def sign(body: str) -> str:
    return base64.b64encode(
        hmac.new(CHANNEL_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    ).decode()


def base_event(event_type, extra):
    return {
        "type": event_type,
        "webhookEventId": str(uuid.uuid4()).replace("-", ""),
        "deliveryContext": {"isRedelivery": False},
        "replyToken": "noreply" + "0" * 26,
        "source": {"type": "user", "userId": TEST_USER_ID},
        "timestamp": int(time.time() * 1000),
        "mode": "active",
        **extra
    }


def send(event):
    body = json.dumps({"destination": "Ctest", "events": [event]}, ensure_ascii=False)
    r = requests.post(WEBHOOK_URL, data=body.encode("utf-8"),
                      headers={"Content-Type": "application/json",
                               "X-Line-Signature": sign(body)})
    return r.status_code


def send_text(text):
    return send(base_event("message", {"message": {"type": "text", "id": str(uuid.uuid4()), "text": text}}))


def send_postback(data):
    return send(base_event("postback", {"postback": {"data": data}}))


steps = [
    ("傳文字「丈量預約」",               lambda: send_text("丈量預約")),
    ("Postback 選日期 2026-05-28",       lambda: send_postback("action=select_date&date=2026-05-28&appt_type=丈量預約")),
    ("Postback 選時段 14:00",            lambda: send_postback("action=select_time&date=2026-05-28&time=14:00&appt_type=丈量預約")),
    ("傳姓名「測試王小明」",              lambda: send_text("測試王小明")),
    ("傳電話「0912000999」",             lambda: send_text("0912000999")),
    ("傳地址「台北市信義區松仁路100號」", lambda: send_text("台北市信義區松仁路100號")),
    ("Postback 確認送出",                lambda: send_postback("action=confirm_booking")),
]

print("== 測試完整預約流程 ==\n")
all_ok = True
for desc, fn in steps:
    code = fn()
    ok = code == 200
    print(f"{'OK' if ok else 'FAIL ' + str(code)}  {desc}")
    if not ok:
        all_ok = False
    time.sleep(1.2)

print("\n" + ("全部通過！" if all_ok else "有錯誤，請查看 Render logs。"))

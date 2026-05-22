import atexit
import os
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask, abort, request
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi
from linebot.v3.webhooks import MessageEvent, PostbackEvent, TextMessageContent, FollowEvent

from handlers.booking import (
    WAITING_CONFIRM, _delete_session, get_supabase,
    push_owner_notification, push_success_to_customer, create_calendar_event,
)
from handlers.message_handler import handle_text_message
from handlers.postback_handler import handle_postback

load_dotenv()

app = Flask(__name__)

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

AUTO_CONFIRM_SECONDS = 10


def auto_confirm_pending():
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=AUTO_CONFIRM_SECONDS)).isoformat()
    try:
        result = (
            get_supabase()
            .table("user_sessions")
            .select("*")
            .eq("state", WAITING_CONFIRM)
            .lt("updated_at", cutoff)
            .execute()
        )
        for session in result.data:
            user_id = session["user_id"]
            try:
                get_supabase().table("bookings").insert({
                    "user_id":   user_id,
                    "appt_type": session["appt_type"],
                    "date":      session["date"],
                    "time":      session["time"],
                    "product":   session.get("product"),
                    "name":      session.get("name", ""),
                    "phone":     session.get("phone", ""),
                    "address":   session.get("address", ""),
                    "status":    "pending",
                }).execute()
                _delete_session(user_id)
                create_calendar_event(session)
                push_owner_notification(
                    session["appt_type"], session["date"], session["time"],
                    session.get("name", ""), session.get("phone", ""),
                    session.get("address", ""), session.get("product"),
                )
                push_success_to_customer(user_id, session)
                print(f"[auto_confirm] {user_id} auto-confirmed")
            except Exception as e:
                print(f"[auto_confirm row error] {e}")
    except Exception as e:
        print(f"[auto_confirm query error] {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(auto_confirm_pending, "interval", seconds=5)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def on_message(event):
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            handle_text_message(event, line_bot_api)
    except Exception as e:
        print(f"[on_message error] {e}")


@handler.add(PostbackEvent)
def on_postback(event):
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            handle_postback(event, line_bot_api)
    except Exception as e:
        print(f"[on_postback error] {e}")


@handler.add(FollowEvent)
def on_follow(event):
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            from linebot.v3.messaging import ReplyMessageRequest
            msg = TextMessage(
                text=(
                    "歡迎來到南島家居 🏠\n\n"
                    "我們專注木地板與建材，\n"
                    "提供選材建議、免費丈量、快速報價服務。\n\n"
                    "你可以直接輸入以下關鍵字快速查詢：\n\n"
                    "📐 輸入「估價」→ 免費報價服務\n"
                    "📷 輸入「案例」→ 看近期施工實例\n"
                    "🪵 輸入「材質」→ 了解各種地板差異\n"
                    "🧹 輸入「保養」→ 地板清潔保養技巧\n\n"
                    "或直接傳訊息給我們，我們會盡快親自回覆 😊"
                )
            )
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[msg])
            )
    except Exception as e:
        print(f"[on_follow error] {e}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

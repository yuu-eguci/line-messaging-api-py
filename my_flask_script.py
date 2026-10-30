"""
line-bot-sdk v3 にちゃんと対応してるよ!
NOTE: このへん↓が参考になるよ!
      https://github.com/line/line-bot-sdk-python/blob/master/examples/flask-echo/app_with_handler.py
"""

from flask import Flask, request, abort, url_for

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    FollowEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
)


# 環境変数取得のため。
import os

# ログを出力するため。
import logging
import sys

app = Flask(__name__)

# ログを標準出力へ。
# app.logger.info で出力するため、レベルは INFO にする。
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

# 大事な情報は環境変数から取得。
handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
configuration = Configuration(
    access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN']
)


# 必須ではないけれど、サーバに上がったとき確認するためにトップページを追加しておきます。
@app.route('/')
def top_page():
    app.logger.info('message: root page')
    return 'Here is root page.'


@app.route('/register', methods=['GET'])
def registration_page():
    user_id = request.args.get('userId')
    if not user_id:
        abort(400)

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        profile = line_bot_api.get_profile(user_id)
        line_bot_api.push_message(
            PushMessageRequest(
                to=profile.user_id,
                messages=[TextMessage(text=f'{profile.display_name} さまを登録しました!\nご利用ありがとうございます!')]
            )
        )

    return 'Please return to LINE app.'


# なにかイベントが発生したとき、この URL へアクセスが行われます。
@app.route('/callback', methods=['POST'])
def callback_post():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    # NOTE: 本文にはユーザのメッセージが入っているため、ログには出しません。
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        # @handler.add した関数が呼び出されます。
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 各 handler の関数の引数 event には、以下のような情報が入っています。
# {
#     "events": [
#         {
#             "type": "message",
#             "replyToken": "********************************",
#             "source": {
#                 "userId": "*********************************",
#                 "type": "user"
#             },
#             "timestamp": 1572247738104,
#             "message": {
#                 "type": "text",
#                 "id": "**************",
#                 "text": "げろげろん"
#             }
#         }
#     ],
#     "destination": "*********************************"
# }
# 情報の取得例。
# event.message.text
# event.source.user_id


# event.type が 'follow' のとき、この関数が呼び出されます。
@handler.add(FollowEvent)
def handle_follow(event):
    app.logger.info("Got Follow event from:" + event.source.user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f'あなたの ID は {event.source.user_id} ですね!')]
            )
        )


# event.type が 'message' のとき、この関数が呼び出されます。
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    app.logger.info("Got Message event from:" + event.source.user_id)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        if event.message.text == 'とーろく':
            register_url = url_for('registration_page', userId=event.source.user_id, _external=True, _scheme='https')
            msg = f'こちらのリンクから登録してください。\n{register_url}'
        else:
            msg = (
                'そのコマンドに該当する機能が見つかりません……。\n'
                'メニューからタップしてご利用ください。'
            )
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=msg)]
            )
        )


if __name__ == '__main__':
    app.run()

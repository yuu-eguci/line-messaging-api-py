from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# 環境変数取得のため。
import os

# ログを出力するため。
import logging
import sys

app = Flask(__name__)

# ログを標準出力へ。heroku logs --tail で確認するため。
# app.logger.info で出力するため、レベルは INFO にする。
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)

# 大事な情報は環境変数から取得。
CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# 必須ではないけれど、サーバに上がったとき確認するためにトップページを追加しておきます。
@app.route('/')
def top_page():
    return 'Here is root page.'


@app.route('/register', methods=['GET'])
def registration_page():
    profile = line_bot_api.get_profile(request.args.get('userId'))
    line_bot_api.push_message(
        profile.user_id,
        TextSendMessage(text=f'{profile.display_name} さまを登録しました!\nご利用ありがとうございます!'))
    return 'Please return to LINE app.'


# ユーザがメッセージを送信したとき、この URL へアクセスが行われます。
@app.route('/callback', methods=['POST'])
def callback_post():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def reply_message(event):
    # 送られてくる情報の構造。
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

    if event.message.text == 'とーろく':
        msg = (
            'こちらのリンクから登録してください。\n'
            f'https://line-messaging-py-py-py.herokuapp.com/register?userId={event.source.user_id}')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg))
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='そのコマンドに該当する機能が見つかりません……。\nメニューからタップしてご利用ください。'))


if __name__ == '__main__':
    app.run()

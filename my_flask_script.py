from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
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

# Get from environment variables.
CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route('/')
def top_page():
    return 'Here is root page.'


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
def handle_message(event):

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

    # userId を取得。
    user_id = event.source.user_id

    # reply のテスト。
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='こちらこーるばっく処理からお送りします:'+event.message.text))

    # push のテスト。 userId を保存しておけば、いつでもユーザへメッセージを送れる。
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text='ぷっしゅめっせーじです。'))


if __name__ == '__main__':
    app.run()

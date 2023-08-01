import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
USER_ID = os.environ['USER_ID']

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

line_bot_api.push_message(
    USER_ID,
    TextSendMessage(text='やあ! 元気?'))

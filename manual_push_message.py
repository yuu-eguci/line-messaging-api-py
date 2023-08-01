import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
)
from linebot.v3.messaging.models.push_message_request import PushMessageRequest

LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
USER_ID = os.environ['USER_ID']

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

with ApiClient(configuration) as api_client:
    api_instance = MessagingApi(api_client)
    push_message_request = PushMessageRequest(
        to=USER_ID,
        messages=[TextMessage(text='やあ! 元気?!')]
    )
    try:
        api_instance.push_message(push_message_request)
    except Exception as e:
        print("Exception when calling MessagingApi->push_message: %s\n" % e)

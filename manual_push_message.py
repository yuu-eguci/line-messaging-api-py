"""
line-bot-sdk v3 にちゃんと対応してるよ!
"""

import os
import sys
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    TextMessage,
)
from linebot.v3.messaging.models.push_message_request import PushMessageRequest


def main():
    configuration = Configuration(access_token=os.environ['LINE_CHANNEL_ACCESS_TOKEN'])

    with ApiClient(configuration) as api_client:
        api_instance = MessagingApi(api_client)
        push_message_request = PushMessageRequest(
            to=os.environ['USER_ID'],
            messages=[TextMessage(text='やあ! 元気?!')]
        )
        try:
            api_instance.push_message(push_message_request)
        except Exception as e:
            print("Exception when calling MessagingApi->push_message: %s\n" % e, file=sys.stderr)
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

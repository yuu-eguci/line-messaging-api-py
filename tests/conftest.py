import os

# テストではダミーの認証情報だけを使います。
os.environ['LINE_CHANNEL_SECRET'] = 'dummy-channel-secret'
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'dummy-channel-access-token'

import base64
import hashlib
import hmac
import json
import logging
from unittest import mock

import pytest

import my_flask_script

CHANNEL_SECRET = 'dummy-channel-secret'
USER_ID = 'U0123456789abcdef0123456789abcdef'
REPLY_TOKEN = 'dummy-reply-token'


def sign(body):
    digest = hmac.new(CHANNEL_SECRET.encode(), body.encode(), hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def webhook_body(event):
    event = {
        'replyToken': REPLY_TOKEN,
        'source': {'type': 'user', 'userId': USER_ID},
        'timestamp': 1572247738104,
        'mode': 'active',
        'webhookEventId': '01H0000000000000000000000',
        'deliveryContext': {'isRedelivery': False},
        **event,
    }
    return json.dumps({'destination': 'Udummy', 'events': [event]}, ensure_ascii=False)


def text_message_body(text):
    return webhook_body({'type': 'message', 'message': {'type': 'text', 'id': '1', 'quoteToken': 'q', 'text': text}})


@pytest.fixture
def client():
    return my_flask_script.app.test_client()


@pytest.fixture
def line_bot_api():
    with mock.patch.object(my_flask_script, 'MessagingApi') as messaging_api:
        yield messaging_api.return_value


def post_callback(client, body, signature):
    return client.post('/callback', data=body, headers={'X-Line-Signature': signature},
                       content_type='application/json')


def replied_text(line_bot_api):
    request = line_bot_api.reply_message.call_args.args[0]
    assert request.reply_token == REPLY_TOKEN
    return request.messages[0].text


def test_top_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'Here is root page.'


def test_callback_rejects_invalid_signature(client, line_bot_api):
    body = text_message_body('こんにちは')

    response = post_callback(client, body, sign(body + 'tampered'))

    assert response.status_code == 400
    line_bot_api.reply_message.assert_not_called()


def test_callback_replies_to_unknown_command(client, line_bot_api):
    body = text_message_body('こんにちは')

    response = post_callback(client, body, sign(body))

    assert response.status_code == 200
    assert response.get_data(as_text=True) == 'OK'
    assert replied_text(line_bot_api).startswith('そのコマンドに該当する機能が見つかりません')


def test_callback_replies_registration_link(client, line_bot_api):
    body = text_message_body('とーろく')

    response = post_callback(client, body, sign(body))

    assert response.status_code == 200
    assert f'https://localhost/register?userId={USER_ID}' in replied_text(line_bot_api)


def test_callback_does_not_log_request_body(client, line_bot_api, caplog):
    body = text_message_body('ひみつのメッセージ')

    with caplog.at_level(logging.INFO, logger=my_flask_script.app.logger.name):
        response = post_callback(client, body, sign(body))

    assert response.status_code == 200
    assert 'ひみつのメッセージ' not in caplog.text


def test_callback_replies_user_id_on_follow(client, line_bot_api):
    body = webhook_body({'type': 'follow', 'follow': {'isUnblocked': False}})

    response = post_callback(client, body, sign(body))

    assert response.status_code == 200
    assert USER_ID in replied_text(line_bot_api)


def test_register_pushes_message(client, line_bot_api):
    line_bot_api.get_profile.return_value = mock.Mock(user_id=USER_ID, display_name='テスト')

    response = client.get('/register', query_string={'userId': USER_ID})

    assert response.status_code == 200
    line_bot_api.get_profile.assert_called_once_with(USER_ID)
    request = line_bot_api.push_message.call_args.args[0]
    assert request.to == USER_ID
    assert request.messages[0].text.startswith('テスト さまを登録しました!')


def test_register_rejects_missing_user_id(client, line_bot_api):
    response = client.get('/register')

    assert response.status_code == 400
    line_bot_api.get_profile.assert_not_called()
    line_bot_api.push_message.assert_not_called()

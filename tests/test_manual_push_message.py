from unittest import mock

import pytest
from linebot.v3.messaging import ApiException

import manual_push_message

USER_ID = 'U0123456789abcdef0123456789abcdef'


@pytest.fixture
def line_bot_api(monkeypatch):
    monkeypatch.setenv('USER_ID', USER_ID)
    with mock.patch.object(manual_push_message, 'MessagingApi') as messaging_api:
        yield messaging_api.return_value


def test_main_pushes_message(line_bot_api):
    assert manual_push_message.main() == 0

    request = line_bot_api.push_message.call_args.args[0]
    assert request.to == USER_ID
    assert request.messages[0].text == 'やあ! 元気?!'


def test_main_returns_1_on_failure(line_bot_api, capsys):
    line_bot_api.push_message.side_effect = ApiException(status=401, reason='Unauthorized')

    assert manual_push_message.main() == 1
    assert 'Exception when calling MessagingApi->push_message' in capsys.readouterr().err

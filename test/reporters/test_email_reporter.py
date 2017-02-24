import pytest

from autograder.reporters import SendAsEmailReporter

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message

@pytest.fixture
def smtp_controller():
    class MessageHandler(Message):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.messages_received = []
        def handle_message(self, message):
            self.messages_received.append(message)
    handler = MessageHandler()
    controller = Controller(handler)
    controller.start()
    controller.messages_recieved = handler.messages_received
    yield controller
    controller.stop()

def fn(id, success, data, global_data):
    return ['foo@example.com', 'bar@example.com']

def test__send_mail(smtp_controller):
    r = SendAsEmailReporter('mailout', 'subject', 'testfile', fn)
    r.setup(
        mailout_email_sender='ping@example.com',
        mailout_email_server=smtp_controller.hostname,
        mailout_email_port=smtp_controller.port,
        mailout_email_user=None,
        mailout_email_password=None)
    r.on_individual_completion('aaa', True, {'testfile': 'aaa\nbbb\nccc'}, {})
    assert [m.get_payload() for m in smtp_controller.messages_recieved] == ['aaa\nbbb\nccc']

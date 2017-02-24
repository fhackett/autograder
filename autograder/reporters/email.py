import autograder as _autograder

import smtplib as _smtplib
import email.mime.text as _mimetext

class SendAsEmailReporter(_autograder.Reporter):
    def __init__(self, name, subject, filename, gen_addresses, dry_run=False, use_tls=False):
        self.name = name
        self.subject = subject
        self.dry_run = dry_run
        self.requirements = {
            '{}-email-password'.format(name): {
                'help': 'The password to the e-mail account you want to send as.',
                'required': False,
                'default': None,
            },
            '{}-email-user'.format(name): {
                'help': 'The user name to use when logging in to the e-mail server.',
                'required': False,
                'default': None,
            },
            '{}-email-sender'.format(name): {
                'help': 'The e-mail to send from.'
            },
            '{}-email-server'.format(name): {
                'help': 'The smtp server you want to use.'
            },
            '{}-email-port'.format(name): {
                'help': 'The port to connect on for the smtp server.',
                'required': False,
                'default': 0,
            },
        }
        self.filename = filename
        self.gen_addresses = gen_addresses
        self.use_tls = use_tls
    def setup(self, **kwargs):
        self.email_password = kwargs['{}_email_password'.format(self.name)]
        self.email_user = kwargs['{}_email_user'.format(self.name)]
        self.email_server = kwargs['{}_email_server'.format(self.name)]
        self.email_port = kwargs['{}_email_port'.format(self.name)]
        self.email_sender = kwargs['{}_email_sender'.format(self.name)]
    def on_individual_completion(self, id, success, data, global_data):
        contents = _mimetext.MIMEText(data[self.filename], 'plain')
        destinations = list(self.gen_addresses(id, success, data, global_data))
        contents['Subject'] = self.subject
        contents['From'] = self.email_sender
        contents['To'] = ', '.join(destinations)
        with _smtplib.SMTP(self.email_server, self.email_port) as s:
            if self.use_tls:
                s.starttls()
            if self.email_user and self.email_password:
                s.login(user=self.email_user, password=self.email_password)
            if self.dry_run:
                print('''\
Send mail
=========
From: {}
To: {}
Content:
{}'''.format(self.email_sender, destinations, contents.as_string()))
            else:
                s.sendmail(self.email_sender, destinations, contents.as_string())

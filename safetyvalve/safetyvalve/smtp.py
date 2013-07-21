
import smtplib

from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.utils import DNS_NAME


class TimeoutEmailBackend(EmailBackend):

    def __init__(self, timeout=None, *args, **kwargs):
        super(TimeoutEmailBackend, self).__init__(*args, **kwargs)
        #EmailBackend.__init__(self, *args, **kwargs)
        self.timeout = timeout or getattr(settings, 'EMAIL_CONNECTION_TIMEOUT', None)

    def open(self):
        """
        Ensures we have a connection to the email server. Returns whether or
        not a new connection was required (True or False).
        """
        if self.connection:
            # Nothing to do if the connection is already open.
            return False
        try:
            # If local_hostname is not specified, socket.getfqdn() gets used.
            # For performance, we use the cached FQDN for local_hostname.
            if self.timeout is None:
                self.connection = smtplib.SMTP(self.host, self.port,
                                               local_hostname=DNS_NAME.get_fqdn())
            else:
                self.connection = smtplib.SMTP(self.host, self.port,
                                               local_hostname=DNS_NAME.get_fqdn(),
                                               timeout=self.timeout)
            if self.use_tls:
                self.connection.ehlo()
                self.connection.starttls()
                self.connection.ehlo()
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise

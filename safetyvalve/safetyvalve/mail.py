#!/usr/bin/env python
# -*- coding: utf-8 -*-


## {{{ http://code.activestate.com/recipes/473810/ (r1)
# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

import logging
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMultiAlternatives
import smtplib

connection = None
connect_retires_max = 5


class Email(EmailMultiAlternatives):
    def send(self, retries=0):
        if self.to == []:
            logging.warn('No recipients set for email "%s"' % self.subject)
        global connection
        if connection is None:
            connection = mail.get_connection()  # Use default email connection
        try:
            connection.send_messages([self])
        except smtplib.SMTPServerDisconnected as e:
            if retries == connect_retires_max:
                raise e
            connection = mail.get_connection()  # Use default email connection
            self.send(retries + 1)


def create_email(subject, body, html=None, from_email=None):
    email = Email()
    email.subject = subject
    email.body = body
    if from_email is None:
        from_email = settings.INSTANCE_NOREPLY_EMAIL
    email.from_email = from_email
    if html is not None:
        email.attach_alternative(html, 'text/html')
    email.to = []
    return email

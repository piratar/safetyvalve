
from django.shortcuts import render
from django.template import Context

from safetyvalve.mail import create_email


def about_us(request):
    return render(request, 'about_us.html', Context({'page_title': 'About Us'}))


def authentication_error(request):
    return render(request, 'authentication_error.html', Context({'page_title': 'Authentication Error'}))


def test_mail(request):

    subject = 'Some Test Message'
    message = 'This is a message!'
    html = '<strong>This</strong> is a message!'
    sender = 'testing@localhost'

    email = create_email(subject, message, html, from_email=sender)
    email.to = ['hardcoded-email-address@localhost']
    email.send()

    return render(request, 'test_email.html')

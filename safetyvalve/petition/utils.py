from html.parser import HTMLParser

from django.utils.html import strip_tags

def convert_petition_to_plaintext_email(content):
    html_parser = HTMLParser.HTMLParser()
    content = content.replace("<br />", "\n")
    content = strip_tags(content)
    content = html_parser.unescape(content)
    content = content.replace("\n", "\n>")

    return content

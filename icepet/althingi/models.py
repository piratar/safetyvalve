# -*- coding: UTF8
from django.db import models

class Session(models.Model):
    session_num = models.IntegerField(unique = True) # IS: Þingnúmer

class Issue(models.Model):
    ISSUE_TYPES = (
        ('l', 'lagafrumvarp'),
        ('a', 'þingsályktunartillaga'),
        ('m', 'fyrirspurn'),
        ('q', 'fyrirspurn til skrifl. svars'),
    )

    session = models.ForeignKey(Session)

    issue_num = models.IntegerField() # IS: Málsnúmer
    issue_type = models.CharField(max_length = 1, choices = ISSUE_TYPES) # IS: Málstegund
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 100)

    # External URLs
    path_html = models.CharField(max_length = 200)
    path_xml = models.CharField(max_length = 200)
    path_rss = models.CharField(max_length = 200)


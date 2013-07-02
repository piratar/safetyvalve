# -*- coding: UTF8
from django.db import models

from petition.models import Petition


class Session(models.Model):
    session_num = models.IntegerField(unique = True) # IS: Þingnúmer

    def __unicode__(self):
        return u'Session %d' % self.session_num


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
    name = models.CharField(max_length = 500)
    description = models.TextField()

    # External URLs
    path_html = models.CharField(max_length = 200)
    path_xml = models.CharField(max_length = 200)
    path_rss = models.CharField(max_length = 200)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        models.Model.save(self, *args, **kwargs)

        if is_new:
            # Create a petition for this issue
            petition = Petition()
            petition.name = self.name
            petition.description = self.description
            petition.description += '\n\nHlekkur: <a href="%s">%s</a>' % (self.path_html, self.path_html)
            petition.save()

    def __unicode__(self):
        return u'Issue: %s' % self.name

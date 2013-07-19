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

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        models.Model.save(self, *args, **kwargs)

        if is_new:
            # Create a petition for this issue
            petition = Petition()
            petition.name = self.name
            petition.description = self.description
            petition.save()

    def __unicode__(self):
        return u'%d (%s)' % (self.issue_num, self.name)

class Document(models.Model):
    issue = models.ForeignKey(Issue)

    doc_num = models.IntegerField()
    doc_type = models.CharField(max_length = 50)
    timing_published = models.DateTimeField()
    is_main = models.BooleanField(default = False)

    path_html = models.CharField(max_length = 500)
    path_pdf = models.CharField(max_length = 500)

    def __unicode__(self):
        return u'%d (%s)' % (self.doc_num, self.doc_type)


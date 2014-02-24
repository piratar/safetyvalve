# -*- coding: utf-8
from django.db import models

from BeautifulSoup import BeautifulSoup
import urllib

from petition.models import Petition, Source


class Session(models.Model):
    session_num = models.IntegerField(unique=True)  # IS: Þingnúmer

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

    issue_num = models.IntegerField()  # IS: Málsnúmer
    issue_type = models.CharField(max_length=1, choices=ISSUE_TYPES)  # IS: Málstegund
    name = models.CharField(max_length=500)
    description = models.TextField()

    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)

        if self.issue_type == 'l':
            external_id = "%s.%s" % (self.session.session_num, self.issue_num)

            if Petition.objects.filter(external_id=external_id).count() == 0:

                althingi_source = Source.objects.get(name='althingi')
                
                # Create a petition for this issue
                petition = Petition()
                petition.source = althingi_source
                petition.external_id = external_id
                petition.name = self.name
                petition.description = self.description
                petition.save()

    def __unicode__(self):
        return u'%d (%s)' % (self.issue_num, self.name)


class Document(models.Model):
    issue = models.ForeignKey(Issue)

    doc_num = models.IntegerField()
    doc_type = models.CharField(max_length=50)
    time_published = models.DateTimeField()
    is_main = models.BooleanField(default=False)

    path_html = models.CharField(max_length=500)
    path_pdf = models.CharField(max_length=500)

    xhtml = models.TextField()

    def save(self, *args, **kwargs):
        if self.is_main and self.issue.issue_type == 'l':
            external_id = "%s.%s" % (self.issue.session.session_num, self.issue.issue_num)

            petition = Petition.objects.get(external_id=external_id)

            # Time of publication (not necessarily creation)
            petition.time_published = self.time_published

            # The resource is essentially a link to some external data.
            petition.resource = self.path_html

            # Get the content of the petition.
            content = urllib.urlopen(self.path_html).read().decode('ISO-8859-1').replace('&nbsp;', ' ')
            soup = BeautifulSoup(content)  # Turn it into proper XML.

            # Remove garbage.
            [s.extract() for s in soup('script')]
            [s.extract() for s in soup('noscript')]
            [s.extract() for s in soup('head')]
            [s.extract() for s in soup('small')]
            [s.extract() for s in soup('hr')]

            # Replace 'html' and 'body' tags'
            body_tag = soup.find('body')
            body_tag.attrs.append(('id', 'body_tag'))
            body_tag.name = 'div'
            html_tag = soup.find('html')
            html_tag.attrs.append(('id', 'html_tag'))
            html_tag.name = 'div'

            self.xhtml = soup.prettify()

            # Final cleanup at text-stage.
            self.xhtml = self.xhtml.replace(' <!-- Tab -->\n  ', '&nbsp;&nbsp;&nbsp;&nbsp;')

            petition.content = self.xhtml

            petition.save()

        models.Model.save(self, *args, **kwargs)

    def __unicode__(self):
        return u'%d (%s)' % (self.doc_num, self.doc_type)

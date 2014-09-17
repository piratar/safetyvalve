from sys import stdout
import urllib
from BeautifulSoup import BeautifulSoup

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from althingi.althingi_settings import CURRENT_SESSION_NUM
from althingi.models import Document
from althingi.models import Issue

from petition.models import Petition
from petition.models import Source

class Command(BaseCommand):

    help = "Imports Althingi's issues and turns them into petitions"

    def handle(self, *args, **options):

        try:
            althingi_source = Source.objects.get(name='althingi')
        except Source.DoesNotExist:
            althingi_source = Source()
            althingi_source.name = 'althingi'
            althingi_source.save()

        issues = Issue.objects.select_related('session').filter(session__session_num=CURRENT_SESSION_NUM)

        for issue in issues:
            if issue.issue_type == 'l' or issue.issue_type == 'a':
                external_id = "%s.%s" % (issue.session.session_num, issue.issue_num)

                if Petition.objects.filter(external_id=external_id).count() == 0:
                    stdout.write("Creating petition for issue %s..." % external_id)
                    stdout.flush()

                    # Create a petition for this issue
                    try:
                        petition = Petition()
                        petition.source = althingi_source
                        petition.external_id = external_id
                        petition.name = issue.name
                        petition.description = issue.description
                        petition.save()

                        stdout.write(" done\n")
                    except Exception as e:
                        stdout.write(" error: %s\n" % e)

                # I was here. About to move the stuff in the remainder of this document to its proper places
                document = Document.objects.get(issue=issue, is_main=True)
                external_id = "%s.%s" % (document.issue.session.session_num, document.issue.issue_num)

                petition = Petition.objects.get(external_id=external_id)

                # Time of publication (not necessarily creation)
                petition.time_published = document.time_published

                # The resource is essentially a link to some external data.
                petition.resource = document.path_html

                # Get the content of the petition.
                content = urllib.urlopen(document.path_html).read().decode('ISO-8859-1').replace('&nbsp;', ' ')
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

                document.xhtml = soup.prettify()

                # Final cleanup at text-stage.
                document.xhtml = document.xhtml.replace(' <!-- Tab -->\n  ', '&nbsp;&nbsp;&nbsp;&nbsp;')

                petition.content = document.xhtml

                petition.save()
 

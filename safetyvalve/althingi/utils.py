# -*- coding: utf-8 -*-

import urllib
from xml.dom import minidom

from models import Session, Issue, Document


#SESSION_URL = 'http://www.althingi.is/altext/xml/loggjafarthing/'
ISSUE_LIST_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/?lthing=%d'
ISSUE_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/thingmal/?lthing=%d&malnr=%d'

CURRENT_SESSION_NUM = 142 # Temporary, while we figure out a wholesome way to auto-detect

#def obtain_sessions():
#    dom = minidom.parse(urllib.urlopen(SESSION_URL))
#
#    raw_things = dom.getElementsByTagName(u'þing')
#
#    things = []
#    for raw_thing in raw_things:
#        thing = {}
#        thing['year'] = raw_thing.getElementsByTagName(u'tímabil')[0].firstChild.nodeValue
#        thing['session_num'] = int(raw_thing.getAttribute(u'númer'))
#        things.append(thing)
#
#    return sorted(things, key=lambda t: t['session_num'])
#
#
#def get_last_session():
#    return obtain_sessions()[-1]

def get_last_session_num(): # Temporary, while we figure out a wholesome way to auto-detect
    return CURRENT_SESSION_NUM

def obtain_issue(session_num):
    dom = minidom.parse(urllib.urlopen(ISSUE_LIST_URL % session_num))
    #dom = minidom.parse(urllib.urlopen(ISSUE_LIST_URL % 142))

    raw_issues = dom.getElementsByTagName(u'mál')

    issues = []
    for raw_issue in raw_issues:
        mal = {}

        mal['name'] = raw_issue.getElementsByTagName(u'málsheiti')[0].firstChild.nodeValue

        mal['description'] = raw_issue.getElementsByTagName(u'efnisgreining')[0].firstChild
        mal['description'] = mal['description'].nodeValue if mal['description'] != None else ''

        mal['issue_type'] = raw_issue.getElementsByTagName(u'málstegund')[0].getAttribute(u'málstegund')

        mal['issue_num'] = int(raw_issue.getAttribute(u'málsnúmer'))

        issues.append(mal)

    return sorted(issues, key=lambda t: t['issue_num'])


def update_issues():
    """Fetch a list of "recent" petitions on Althingi and update our database
    accordingly.
    """

    #thing = get_last_session()
    session_num = get_last_session_num()

    session, created = Session.objects.get_or_create(session_num = session_num)
    if created:
        print 'Added session: %s' % session_num
    
    #limit = 5
    #print 'NOTA BENE: Currently, we only fetch the last %d thingmal, for quicker updates' % limit
    #for mal in reversed(obtain_issue(thing)[-limit:]):
    for mal in reversed(obtain_issue(session_num)):
        issue, created = Issue.objects.get_or_create(name=mal['name'], session=session, issue_num=mal['issue_num'])
        if not created:
            continue
        issue.name = mal['name']
        issue.description = mal['description']
        issue.issue_type = mal['issue_type']
        issue.save()

        print "Added issue: %s" % issue

        # Import the issue's documents.
        issue_xml = minidom.parse(urllib.urlopen(ISSUE_URL % (session_num, issue.issue_num))) 
        docs_xml = issue_xml.getElementsByTagName(u'þingskjöl')[0].getElementsByTagName(u'þingskjal');

        lowest_doc_num = 0 # Lowest document number will always be the main document of the issue.
        for doc_xml in docs_xml:
            # Make sure that this is indeed the correct issue.
            if int(doc_xml.getAttribute(u'málsnúmer')) != issue.issue_num or int(doc_xml.getAttribute(u'þingnúmer')) != session_num:
                continue

            doc_num = int(doc_xml.getAttribute(u'skjalsnúmer'))
            doc_type = doc_xml.getElementsByTagName(u'skjalategund')[0].firstChild.nodeValue
            timing_published = doc_xml.getElementsByTagName(u'útbýting')[0].firstChild.nodeValue + "+00:00"

            path_html = doc_xml.getElementsByTagName(u'slóð')[0].getElementsByTagName(u'html')[0].firstChild.nodeValue
            path_pdf = doc_xml.getElementsByTagName(u'slóð')[0].getElementsByTagName(u'pdf')[0].firstChild.nodeValue

            if lowest_doc_num == 0:
                lowest_doc_num = doc_num
            elif lowest_doc_num > doc_num:
                lowest_doc_num = doc_num

            Document.objects.get_or_create(
                doc_num=doc_num,
                doc_type=doc_type,
                timing_published=timing_published,
                path_html=path_html,
                path_pdf=path_pdf,
                issue=issue,
            )

            print "- Added document: %d" % doc_num

        main_doc = Document.objects.get(issue=issue, doc_num=lowest_doc_num)
        main_doc.is_main = True
        main_doc.save()

        print "- Main document determined to be: %d" % lowest_doc_num


    '''
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
    '''

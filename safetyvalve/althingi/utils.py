# -*- coding: utf-8 -*-

import urllib
from xml.dom import minidom

from models import Session, Issue, Document

ISSUE_LIST_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/?lthing=%d'
ISSUE_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/thingmal/?lthing=%d&malnr=%d'

CURRENT_SESSION_NUM = 142 # Temporary, while we figure out a wholesome way to auto-detect

def get_last_session_num():
    return CURRENT_SESSION_NUM # Temporary, while we figure out a wholesome way to auto-detect

def update_issues():
    """Fetch a list of "recent" petitions on Althingi and update our database
    accordingly.
    """

    session_num = get_last_session_num()

    session, created = Session.objects.get_or_create(session_num = session_num)
    if created:
        print 'Added session: %s' % session_num
    else:
        print 'Already have session: %s' % session_num

    issue_list_xml = minidom.parse(urllib.urlopen(ISSUE_LIST_URL % session_num))

    issues_xml = issue_list_xml.getElementsByTagName(u'mál')

    for issue_xml in issues_xml:

        name = issue_xml.getElementsByTagName(u'málsheiti')[0].firstChild.nodeValue

        description = issue_xml.getElementsByTagName(u'efnisgreining')[0].firstChild
        description = description.nodeValue if description != None else ''

        issue_type = issue_xml.getElementsByTagName(u'málstegund')[0].getAttribute(u'málstegund')

        issue_num = int(issue_xml.getAttribute(u'málsnúmer'))

        issue_try = Issue.objects.filter(issue_num=issue_num, session=session)
        if issue_try.count() > 0:
            issue = issue_try[0]

            print 'Already have issue: %s' % issue
        else:
            issue = Issue()
            issue.issue_num = issue_num
            issue.issue_type = issue_type
            issue.name = name
            issue.description = description
            issue.session = session
            issue.save()

            print 'Added issue: %s' % issue

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

            doc_try = Document.objects.filter(doc_num=doc_num, issue=issue)
            if doc_try.count() > 0:
                doc = doc_try[0]

                print 'Already have document: %s' % doc
            else:
                doc = Document()
                doc.doc_num = doc_num
                doc.doc_type = doc_type
                doc.timing_published = timing_published
                doc.path_html = path_html
                doc.path_pdf = path_pdf
                doc.issue = issue
                doc.save()

                print '- Added document: %s' % doc

        main_doc = Document.objects.get(issue=issue, doc_num=lowest_doc_num)
        main_doc.is_main = True
        main_doc.save()

        print '- Main document determined to be: %s' % main_doc


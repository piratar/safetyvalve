# -*- coding: utf-8 -*-
from __future__ import absolute_import

import urllib
from xml.dom import minidom

from .models import Session, Issue, Document, Parliamentarian, Parliamentarian
from .althingi_settings import *

ISSUE_LIST_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/?lthing=%d'
ISSUE_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/thingmal/?lthing=%d&malnr=%d'
PARLIAMENTARIANS_URL = 'http://www.althingi.is/altext/xml/thingmenn/'
PARLIAMENTARIAN_DETAILS_URL = 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/thingseta/?nr=%d'


def get_last_session_num():
    return CURRENT_SESSION_NUM  # Temporary, while we figure out a wholesome way to auto-detect


def update_issues():
    """Fetch a list of "recent" petitions on Althingi and update our database
    accordingly.
    """

    session_num = get_last_session_num()

    session, created = Session.objects.get_or_create(session_num=session_num)
    if created:
        print 'Added session: %s' % session_num
    else:
        print 'Already have session: %s' % session_num

    issue_list_xml = minidom.parse(urllib.urlopen(ISSUE_LIST_URL % session_num))

    issues_xml = issue_list_xml.getElementsByTagName(u'mál')

    for issue_xml in issues_xml:

        name = issue_xml.getElementsByTagName(u'málsheiti')[0].firstChild.nodeValue

        description = issue_xml.getElementsByTagName(u'efnisgreining')[0].firstChild
        description = description.nodeValue if description != None else 'engin lýsing útgefin'

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
        docs_xml = issue_xml.getElementsByTagName(u'þingskjöl')[0].getElementsByTagName(u'þingskjal')

        lowest_doc_num = 0  # Lowest document number will always be the main document of the issue.
        for doc_xml in docs_xml:
            # Make sure that this is indeed the correct issue.
            if int(doc_xml.getAttribute(u'málsnúmer')) != issue.issue_num or int(doc_xml.getAttribute(u'þingnúmer')) != session_num:
                continue

            doc_num = int(doc_xml.getAttribute(u'skjalsnúmer'))
            doc_type = doc_xml.getElementsByTagName(u'skjalategund')[0].firstChild.nodeValue
            time_published = doc_xml.getElementsByTagName(u'útbýting')[0].firstChild.nodeValue + "+00:00"

            paths_xml =  doc_xml.getElementsByTagName(u'slóð')
            html_paths_xml = paths_xml[0].getElementsByTagName(u'html') 
            pdf_paths_xml = paths_xml[0].getElementsByTagName(u'pdf')
            if len(html_paths_xml) == 0:
                print 'Document not published: %d' % doc_num
                continue

            path_html = html_paths_xml[0].firstChild.nodeValue
            path_pdf = pdf_paths_xml[0].firstChild.nodeValue

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
                doc.time_published = time_published
                doc.path_html = path_html
                doc.path_pdf = path_pdf
                doc.issue = issue
                doc.save()

                print '- Added document: %s' % doc

        main_doc = Document.objects.get(issue=issue, doc_num=lowest_doc_num)
        main_doc.is_main = True
        main_doc.save()

        print '- Main document determined to be: %s' % main_doc


def update_parliamentarians(update_existing=True):
    if str(update_existing).lower() == "false":
        update_existing = False

    parlimentarians_list_xml = minidom.parse(urllib.urlopen(PARLIAMENTARIANS_URL))
    parliamentarians_xml = parlimentarians_list_xml.getElementsByTagName(u'þingmaður')

    for parliamentarian_xml in parliamentarians_xml:
        parliamentarian_id = int(parliamentarian_xml.getAttribute(u'id'))
        parliamentarian_name = xml_value_or_empty_string(parliamentarian_xml.getElementsByTagName('nafn')[0].firstChild)

        try:
            parliamentarian = Parliamentarian.objects.get(parliamentarian_id=parliamentarian_id)
        except Parliamentarian.DoesNotExist:
            parliamentarian = Parliamentarian()

        if parliamentarian.id != None and update_existing == False:
            continue

        parliamentarian.parliamentarian_id = parliamentarian_id
        parliamentarian.name = parliamentarian_name.strip()

        try:
            parliamentarian_detail_xml = minidom.parse(urllib.urlopen(PARLIAMENTARIAN_DETAILS_URL % parliamentarian_id))

            most_recent_session = None
            sessions = parliamentarian_detail_xml.getElementsByTagName(u'þingsetur')[0].getElementsByTagName(u'þingseta')

            for session in sessions:
                session_id = xml_value_or_zero(session.getElementsByTagName(u'þing')[0].firstChild)
                
                if most_recent_session is None:
                    most_recent_session = session

                if xml_value_or_zero(most_recent_session.getElementsByTagName(u'þing')[0].firstChild) < session_id:
                    most_recent_session = session

            if most_recent_session:
                parliamentarian.constituency_id = int(xml_value_or_zero(most_recent_session.getElementsByTagName(u'kjördæmanúmer')[0].firstChild))
                parliamentarian.name_abbreviated = xml_value_or_empty_string(most_recent_session.getElementsByTagName(u'skammstöfun')[0].firstChild).strip()
                parliamentarian.party = xml_value_or_empty_string(most_recent_session.getElementsByTagName(u'þingflokkur')[0].firstChild).strip()
                parliamentarian.constituency = xml_value_or_empty_string(most_recent_session.getElementsByTagName(u'kjördæmi')[0].firstChild).strip()
                parliamentarian.seat_number = xml_value_or_zero(most_recent_session.getElementsByTagName(u'þingsalssæti')[0].firstChild)
                parliamentarian.most_recent_session_served = xml_value_or_zero(most_recent_session.getElementsByTagName(u'þing')[0].firstChild)


        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            print type(ex).__name__ + ': ' + PARLIAMENTARIAN_DETAILS_URL % parliamentarian_id
            print ""

        print parliamentarian
        parliamentarian.save()

    return


def xml_value_or_empty_string(value):
    if value:
        return value.nodeValue
    else:
        return""


def xml_value_or_zero(value):
    if value:
        return value.nodeValue
    else:
        return 0

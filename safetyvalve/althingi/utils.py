# -*- coding: utf-8 -*-
from __future__ import absolute_import

import urllib
from xml.dom import minidom

from .models import Session, Issue, IssueVotingRound, Document, Parliamentarian, ParliamentarianSession
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
        parliamentarian_name = xml_value_or_empty_string(parliamentarian_xml.getElementsByTagName(u'nafn')[0].firstChild)

        try:
            parliamentarian = Parliamentarian.objects.get(parliamentarian_id=parliamentarian_id)
        except Parliamentarian.DoesNotExist:
            parliamentarian = Parliamentarian()

        if parliamentarian.id is not None and update_existing is False:
            continue

        parliamentarian.parliamentarian_id = parliamentarian_id
        parliamentarian.name = parliamentarian_name.strip()

        print parliamentarian
        parliamentarian.save()

    return

def update_parliamentarian_sessions():
    parliamentarians = Parliamentarian.objects.all()

    for parliamentarian in parliamentarians:

        try:
            parliamentarian_detail_xml = minidom.parse(urllib.urlopen(PARLIAMENTARIAN_DETAILS_URL % parliamentarian.parliamentarian_id))
            sessions_xml = parliamentarian_detail_xml.getElementsByTagName(u'þingsetur')[0].getElementsByTagName(u'þingseta')

            for session_xml in sessions_xml:
                session_num = xml_value_or_negative_int(
                    session_xml.getElementsByTagName(u'þing')[0].firstChild
                )

                try:
                    session = ParliamentarianSession.objects.get(parliamentarian=parliamentarian, session_num=session_num)
                except ParliamentarianSession.DoesNotExist:
                    session = ParliamentarianSession()

                session.parliamentarian = parliamentarian

                session.session_num = session_num

                session.constituency_id = xml_value_or_negative_int(
                    session_xml.getElementsByTagName(u'kjördæmanúmer')[0].firstChild
                )
                session.name_abbreviation = xml_value_or_empty_string(
                    session_xml.getElementsByTagName(u'skammstöfun')[0].firstChild
                ).strip()
                session.party = xml_value_or_empty_string(
                    session_xml.getElementsByTagName(u'þingflokkur')[0].firstChild
                ).strip()
                session.constituency = xml_value_or_empty_string(
                    session_xml.getElementsByTagName(u'kjördæmi')[0].firstChild
                ).strip()
                session.seat_number = xml_value_or_negative_int(
                    session_xml.getElementsByTagName(u'þingsalssæti')[0].firstChild
                )
                session.most_recent_session_served = xml_value_or_negative_int(
                    session_xml.getElementsByTagName(u'þing')[0].firstChild
                )

                session.save()

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            print type(ex).__name__ + ': ' + PARLIAMENTARIAN_DETAILS_URL % parliamentarian.parliamentarian_id
            print ex
            print ""

    return

def update_voting_rounds(session_number=-1):

    if session_number == -1:
        session_number = get_last_session_num()

    issues = Issue.objects.filter(session__session_num=session_number)
    for issue in issues:
        #this should go to logging or something later, should be more clean
        print issue

        issue_xml = minidom.parse(urllib.urlopen(ISSUE_URL % (session_number, issue.issue_num)))
        voting_rounds_xml = issue_xml.getElementsByTagName(u'atkvæðagreiðslur')[0].getElementsByTagName(u'atkvæðagreiðsla')

        for voting_round_xml in voting_rounds_xml:
            round_number = int(voting_round_xml.getAttribute(u'atkvæðagreiðslunúmer'))
            round_type = xml_value_or_empty_string(voting_round_xml.getElementsByTagName(u'tegund')[0].firstChild)
            round_details = xml_value_or_empty_string(voting_round_xml.getElementsByTagName(u'nánar')[0].firstChild)
            votes_casted_time = voting_round_xml.getElementsByTagName(u'tími')[0].firstChild.nodeValue + "+00:00"

            # parliamentarian votes are not always present. we check for the yes node to see if they are present.
            yes_votes_xml = voting_round_xml.getElementsByTagName(u'já')
            has_parliamentarian_votes = False

            if len(yes_votes_xml) > 0:
                has_parliamentarian_votes = True

            # determines if final round of voting, i.e. bill is final
            final_round = False

            if round_type == 'Frv.' and 'svo breytt' in round_details:
                final_round = True

            try:
                voting_round = IssueVotingRound.objects.get(issue=issue, round_number=round_number)
            except IssueVotingRound.DoesNotExist:
                voting_round = IssueVotingRound()

            voting_round.issue = issue
            voting_round.round_number = round_number
            voting_round.round_type = round_type
            voting_round.round_details = round_details
            voting_round.votes_casted_time = votes_casted_time
            voting_round.has_parliamentarian_votes = has_parliamentarian_votes
            voting_round.final_round = final_round

            voting_round.save()

    return


def xml_value_or_empty_string(value):
    if value:
        return value.nodeValue
    else:
        return""


def xml_value_or_negative_int(value):
    if value:
        return value.nodeValue
    else:
        return -1

# -*- coding: utf-8 -*-

import urllib
from xml.dom import minidom

from models import Session, Issue


LOGGJAFATHING_URL = 'http://www.althingi.is/altext/xml/loggjafarthing/'
THINGMALALISTI_URL = 'http://www.althingi.is/altext/xml/thingmalalisti/?lthing=%d'


def obtain_loggjafathings():
    dom = minidom.parse(urllib.urlopen(LOGGJAFATHING_URL))

    raw_things = dom.getElementsByTagName(u'þing')

    things = []
    for raw_thing in raw_things:
        thing = {}
        thing['year'] = raw_thing.getElementsByTagName(u'tímabil')[0].firstChild.nodeValue
        thing['session_num'] = int(raw_thing.getAttribute(u'númer'))
        things.append(thing)

    return sorted(things, key=lambda t: t['session_num'])


def get_last_loggjafathing():
    return obtain_loggjafathings()[-1]


def obtain_thingmal(thing):
    dom = minidom.parse(urllib.urlopen(THINGMALALISTI_URL % thing['session_num']))

    raw_thingmals = dom.getElementsByTagName(u'mál')

    thingmals = []
    for raw_thingmal in raw_thingmals:
        mal = {}
        mal['name'] = raw_thingmal.getElementsByTagName(u'málsheiti')[0].firstChild.nodeValue
#        mal[''] = raw_thingmal.getElementsByTagName(u'')[0].firstChild.nodeValue
#        mal[''] = raw_thingmal.getElementsByTagName(u'')[0].firstChild.nodeValue
        mal['issue_num'] = int(raw_thingmal.getAttribute(u'málsnúmer'))
#        mal[''] = int(raw_thingmal.getAttribute(u''))
#        mal[''] = int(raw_thingmal.getAttribute(u''))
        thingmals.append(mal)

    return sorted(thingmals, key=lambda t: t['issue_num'])


def update_issues():
    """Fetch a list of "recent" petitions on Althingi and update our database
    accordingly.
    """

    thing = get_last_loggjafathing()
    session, created = Session.objects.get_or_create(session_num=thing['session_num'])
    if created:
        print 'New Thing created!'
    
    limit = 5
    print 'NOTA BENE: Currently, we only fetch the last %d thingmal, for quicker updates' % limit
    for mal in reversed(obtain_thingmal(thing)[-limit:]):
        issue, created = Issue.objects.get_or_create(name=mal['name'], session=session, issue_num=mal['issue_num'])
        if not created:
            break
        issue.name = mal['name']
        issue.save()

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

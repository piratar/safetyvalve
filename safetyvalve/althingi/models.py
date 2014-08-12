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
    final_vote_complete = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Session: (%d) | %d (%s)' % (self.session.session_num, self.issue_num, self.name)


class IssueVotingRound(models.Model):
    issue = models.ForeignKey(Issue)
    round_number = models.IntegerField()
    round_type = models.CharField(max_length=100)
    round_details = models.CharField(max_length=100)
    votes_casted_time = models.DateTimeField()
    has_parliamentarian_votes = models.BooleanField(default=0)
    final_round = models.BooleanField(default=0)

    def __unicode__(self):
        return u'vround number: %d | round_type: %s | round_details: %s | cast time: %s | parliamentarian votes: %s | final: %s' % (
            self.round_number,
            self.round_type,
            self.round_details,
            self.votes_casted_time,
            self.has_parliamentarian_votes,
            self.final_round)


class Document(models.Model):
    issue = models.ForeignKey(Issue)

    doc_num = models.IntegerField()
    doc_type = models.CharField(max_length=50)
    time_published = models.DateTimeField()
    is_main = models.BooleanField(default=False)

    path_html = models.CharField(max_length=500)
    path_pdf = models.CharField(max_length=500)

    xhtml = models.TextField()

    def __unicode__(self):
        return u'%d (%s)' % (self.doc_num, self.doc_type)


class Parliamentarian (models.Model):
    #note that the field parliamentarian_id below refers to the id that aþingi uses
    #to refer to the þingmaður, and not the primary key generated for each row
    parliamentarian_id = models.IntegerField()
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u'db_id: %s | parliamentarian_id: (%s) | name: %s' % (
            self.id,
            self.parliamentarian_id,
            self.name)
            #self.party,
            #self.constituency)


class ParliamentarianSession (models.Model):
    parliamentarian = models.ForeignKey(Parliamentarian)
    constituency_id = models.IntegerField(default=0)
    seat_number = models.IntegerField(default=0)
    session_num = models.IntegerField()

    # abbreviation is stored in a different place in the xml, and therefore could change by term
    name_abbreviation = models.CharField(max_length=20, default="")
    party = models.CharField(max_length=200, default="")
    constituency = models.CharField(max_length=250, default="")

    def __unicode__(self):
        return u'db_id: %s | parliamentarian_id: (%s) | name: %s | session_num: %s | abbrev: %s | party: %s | constituency_id: %s | constituency: %s' % (
            self.id,
            self.parliamentarian.parliamentarian_id,
            self.parliamentarian.name,
            self.session_num,
            self.name_abbreviation,
            self.party,
            self.constituency_id,
            self.constituency)


class ParliamentarianVote (models.Model):
    VOTE_TYPES = (
        ('j', 'já'),
        ('n', 'nei'),
        ('sh', 'sátuhjá'),
        ('gea', 'greiðirekkiatkvæði')
    )

    issue_voting_round = models.ForeignKey(IssueVotingRound)
    parliamentarian = models.ForeignKey(Parliamentarian)
    vote_type = models.CharField(max_length=3, choices=VOTE_TYPES)

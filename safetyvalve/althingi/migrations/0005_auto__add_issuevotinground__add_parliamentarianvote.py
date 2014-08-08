# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IssueVotingRound'
        db.create_table(u'althingi_issuevotinground', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voting_round_number', self.gf('django.db.models.fields.IntegerField')()),
            ('round_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('round_details', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('vost_casted_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('final_round', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'althingi', ['IssueVotingRound'])

        # Adding model 'ParliamentarianVote'
        db.create_table(u'althingi_parliamentarianvote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue_voting_round', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['althingi.IssueVotingRound'])),
            ('parliamentarian', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['althingi.Parliamentarian'])),
            ('vote_type', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal(u'althingi', ['ParliamentarianVote'])


    def backwards(self, orm):
        # Deleting model 'IssueVotingRound'
        db.delete_table(u'althingi_issuevotinground')

        # Deleting model 'ParliamentarianVote'
        db.delete_table(u'althingi_parliamentarianvote')


    models = {
        u'althingi.document': {
            'Meta': {'object_name': 'Document'},
            'doc_num': ('django.db.models.fields.IntegerField', [], {}),
            'doc_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Issue']"}),
            'path_html': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'path_pdf': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'time_published': ('django.db.models.fields.DateTimeField', [], {}),
            'xhtml': ('django.db.models.fields.TextField', [], {})
        },
        u'althingi.issue': {
            'Meta': {'object_name': 'Issue'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'final_vote_complete': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_num': ('django.db.models.fields.IntegerField', [], {}),
            'issue_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Session']"})
        },
        u'althingi.issuevotinground': {
            'Meta': {'object_name': 'IssueVotingRound'},
            'final_round': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'round_details': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'round_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'vost_casted_time': ('django.db.models.fields.DateTimeField', [], {}),
            'voting_round_number': ('django.db.models.fields.IntegerField', [], {})
        },
        u'althingi.parliamentarian': {
            'Meta': {'object_name': 'Parliamentarian'},
            'constituency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            'constituency_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'most_recent_session_served': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_abbreviation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'}),
            'parliamentarian_id': ('django.db.models.fields.IntegerField', [], {}),
            'party': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'seat_number': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'althingi.parliamentarianvote': {
            'Meta': {'object_name': 'ParliamentarianVote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_voting_round': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.IssueVotingRound']"}),
            'parliamentarian': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Parliamentarian']"}),
            'vote_type': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'althingi.session': {
            'Meta': {'object_name': 'Session'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_num': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['althingi']
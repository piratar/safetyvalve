# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ParliamentarianSession.constituency_id'
        db.delete_column(u'althingi_parliamentariansession', 'constituency_id')

        # Deleting field 'ParliamentarianSession.session_num'
        db.delete_column(u'althingi_parliamentariansession', 'session_num')

        # Adding field 'ParliamentarianSession.session'
        db.add_column(u'althingi_parliamentariansession', 'session',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['althingi.Session']),
                      keep_default=False)


        # Changing field 'ParliamentarianSession.name_abbreviation'
        db.alter_column(u'althingi_parliamentariansession', 'name_abbreviation', self.gf('django.db.models.fields.CharField')(max_length=15))

    def backwards(self, orm):
        # Adding field 'ParliamentarianSession.constituency_id'
        db.add_column(u'althingi_parliamentariansession', 'constituency_id',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ParliamentarianSession.session_num'
        db.add_column(u'althingi_parliamentariansession', 'session_num',
                      self.gf('django.db.models.fields.IntegerField')(default=143),
                      keep_default=False)

        # Deleting field 'ParliamentarianSession.session'
        db.delete_column(u'althingi_parliamentariansession', 'session_id')


        # Changing field 'ParliamentarianSession.name_abbreviation'
        db.alter_column(u'althingi_parliamentariansession', 'name_abbreviation', self.gf('django.db.models.fields.CharField')(max_length=20))

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
            'has_parliamentarian_votes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Issue']"}),
            'round_details': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'round_number': ('django.db.models.fields.IntegerField', [], {}),
            'round_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'votes_casted_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'althingi.parliamentarian': {
            'Meta': {'object_name': 'Parliamentarian'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parliamentarian_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'althingi.parliamentariansession': {
            'Meta': {'object_name': 'ParliamentarianSession'},
            'constituency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_abbreviation': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '15'}),
            'parliamentarian': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Parliamentarian']"}),
            'party': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'seat_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Session']"})
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
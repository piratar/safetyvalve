# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Parliamentarian'
        db.create_table(u'althingi_parliamentarian', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parliamentarian_id', self.gf('django.db.models.fields.IntegerField')()),
            ('constituency_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_abbreviation', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('party', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('constituency', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('seat_number', self.gf('django.db.models.fields.IntegerField')()),
            ('most_recent_term', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'althingi', ['Parliamentarian'])

        # Adding field 'Issue.final_vote_complete'
        db.add_column(u'althingi_issue', 'final_vote_complete',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Parliamentarian'
        db.delete_table(u'althingi_parliamentarian')

        # Deleting field 'Issue.final_vote_complete'
        db.delete_column(u'althingi_issue', 'final_vote_complete')


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
        u'althingi.parliamentarian': {
            'Meta': {'object_name': 'Parliamentarian'},
            'constituency': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'constituency_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'most_recent_term': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'parliamentarian_id': ('django.db.models.fields.IntegerField', [], {}),
            'party': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'seat_number': ('django.db.models.fields.IntegerField', [], {})
        },
        u'althingi.session': {
            'Meta': {'object_name': 'Session'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_num': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['althingi']
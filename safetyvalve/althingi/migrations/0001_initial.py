# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Session'
        db.create_table(u'althingi_session', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_num', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'althingi', ['Session'])

        # Adding model 'Issue'
        db.create_table(u'althingi_issue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['althingi.Session'])),
            ('issue_num', self.gf('django.db.models.fields.IntegerField')()),
            ('issue_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'althingi', ['Issue'])

        # Adding model 'Document'
        db.create_table(u'althingi_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['althingi.Issue'])),
            ('doc_num', self.gf('django.db.models.fields.IntegerField')()),
            ('doc_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('time_published', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_main', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('path_html', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('path_pdf', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('xhtml', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'althingi', ['Document'])


    def backwards(self, orm):
        # Deleting model 'Session'
        db.delete_table(u'althingi_session')

        # Deleting model 'Issue'
        db.delete_table(u'althingi_issue')

        # Deleting model 'Document'
        db.delete_table(u'althingi_document')


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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_num': ('django.db.models.fields.IntegerField', [], {}),
            'issue_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['althingi.Session']"})
        },
        u'althingi.session': {
            'Meta': {'object_name': 'Session'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'session_num': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['althingi']
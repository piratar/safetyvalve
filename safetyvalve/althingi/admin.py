from django.contrib import admin
from models import Session, Issue, Document


class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_num')


class IssueAdmin(admin.ModelAdmin):
    list_display = ('name', 'issue_num', 'issue_type', 'description', 'session')


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_num', 'doc_type', 'timing_published', 'is_main', 'path_html', 'path_pdf', 'xhtml')


admin.site.register(Session, SessionAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Document, DocumentAdmin)

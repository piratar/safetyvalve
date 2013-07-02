from django.contrib import admin
from models import Session, Issue


class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_num')


class IssueAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'issue_num', 'issue_type', 'session')


admin.site.register(Session, SessionAdmin)
admin.site.register(Issue, IssueAdmin)

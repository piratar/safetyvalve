from django.contrib import admin
from petition.models import Petition, Signature


class PetitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_created', 'last_updated')
    date_hierarchy = 'timing_published'


class SignatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'show_public', 'petition', 'authentication', 'comment', 'date_created')
    date_hierarchy = 'date_created'


admin.site.register(Petition, PetitionAdmin)
admin.site.register(Signature, SignatureAdmin)

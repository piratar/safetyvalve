from django.contrib import admin
from petition.models import Petition, Signature


class PetitionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_created', 'last_updated')


class SignatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'petition', 'authentication', 'comment', 'date_created')


admin.site.register(Petition, PetitionAdmin)
admin.site.register(Signature, SignatureAdmin)

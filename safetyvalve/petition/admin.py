from django.contrib import admin
from petition.models import Petition

class PetitionAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'date_created', 'last_updated')

admin.site.register(Petition, PetitionAdmin)
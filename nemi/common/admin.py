
from django.contrib import admin

from models import DefinitionsDOM

class DefinitionsDOMAdmin(admin.ModelAdmin):
    pass

admin.site.register(DefinitionsDOM, DefinitionsDOMAdmin)

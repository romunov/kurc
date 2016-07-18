from django.contrib import admin

# Register your models here.
from .models import Docs


class DocsInAdmin(admin.ModelAdmin):
    fields = ('docname', 'doccount', 'active')


admin.site.register(Docs, DocsInAdmin)

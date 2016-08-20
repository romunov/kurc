from django.contrib import admin
# Register your models here.
from .models import Docs, UploadedDocs


def change_to_active(modeladmin, request, queryset):
    queryset.update(active=1)

change_to_active.short_description = 'Turn active on'


def change_from_active(modeladmin, request, queryset):
    queryset.update(active=0)


change_from_active.short_description = 'Turn active off'


class DocsInAdmin(admin.ModelAdmin):
    fields = ('docname', 'doccount', 'active')
    list_display = ('docname', 'doccount', 'active')
    list_filter = ('active', 'doccount')
    actions = [change_from_active, change_to_active]


class UploadedDocsAdmin(admin.ModelAdmin):
    fields = ('id', 'docname', 'docfile', 'docuser', 'doctime')
    list_display = ('docname', 'docfile', 'docuser')
    list_filter = ('docname', 'docfile')


admin.site.register(Docs, DocsInAdmin)
admin.site.register(UploadedDocs, UploadedDocsAdmin)

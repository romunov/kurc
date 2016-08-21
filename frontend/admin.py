from django.contrib import admin
# Register your models here.
from .models import Docs, UploadedDocs, Recipients


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
    fields = ('docname', 'docfile', 'docuser')
    list_display = ('docname', 'docfile', 'docuser', 'doctime')
    list_filter = ('docname', 'docfile', 'docuser', 'doctime')


def sending_on(modeladmin, request, queryset):
    queryset.update(active=True)


sending_on.short_description = 'Start sending emails'


def sending_off(modeladmin, request, queryset):
    queryset.update(active=False)


sending_off.short_description = 'Stop sending emails'


class RecipientsAdmin(admin.ModelAdmin):
    fields = ('email', 'active')
    list_display = ('email', 'active')
    list_filter = ('email', 'active')
    actions = [sending_on, sending_off]


admin.site.register(Docs, DocsInAdmin)
admin.site.register(UploadedDocs, UploadedDocsAdmin)
admin.site.register(Recipients, RecipientsAdmin)

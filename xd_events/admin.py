from django.contrib import admin
from xd_events.models import EventParameter, EventType, Event


class EventParameterAdmin(admin.ModelAdmin):
    list_display = ("key", "value")
    search_fields = ("key", "value")


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "processed_at", "user", "entity")
    search_fields = ("type__name",)


admin.site.register(EventParameter, EventParameterAdmin)
admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)

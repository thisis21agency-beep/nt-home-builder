from django.contrib import admin
from .models import Homepage, Section, SectionItem, HomepageSnapshot

class SectionItemInline(admin.TabularInline):
    model=SectionItem
    extra=0
    fields=('sequence','enabled','title','target_url','product_ref')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display=('name','page','sequence','section_type','enabled','source_type')
    list_filter=('page','section_type','enabled','source_type')
    search_fields=('name','heading','key','category_key')
    ordering=('page','sequence')
    inlines=[SectionItemInline]

@admin.register(Homepage)
class HomepageAdmin(admin.ModelAdmin):
    list_display=('name','code','active','published_revision','published_at')
    readonly_fields=('preview_token','published_revision','published_at','published_by','published_payload')

@admin.register(HomepageSnapshot)
class SnapshotAdmin(admin.ModelAdmin):
    list_display=('page','revision','published_at','published_by')
    readonly_fields=('page','revision','payload','published_at','published_by')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

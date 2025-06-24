from django.contrib import admin
from .models import EverydayCategory


@admin.register(EverydayCategory)
class EverydayCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at', 'updated_at']
    search_fields = ['name', 'created_by__username']
    list_filter = ['created_at', 'created_by']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['name']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

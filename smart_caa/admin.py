from django.contrib import admin
from .models import EverydayCategory, Pictogram


class PictogramInline(admin.TabularInline):
    model = Pictogram
    extra = 0
    fields = ['name', 'is_active', 'image', 'audio']
    readonly_fields = []
    

@admin.register(EverydayCategory)
class EverydayCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_by', 'created_at', 'updated_at']
    search_fields = ['name', 'created_by__username']
    list_filter = ['is_active', 'created_at', 'created_by']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['name']
    inlines = [PictogramInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Pictogram)
class PictogramAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_by', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'created_by__username']
    list_filter = ['is_active', 'category', 'created_at', 'created_by']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Arquivos', {
            'fields': ('image', 'audio')
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Otimiza as consultas incluindo a categoria relacionada"""
        return super().get_queryset(request).select_related('category', 'created_by')

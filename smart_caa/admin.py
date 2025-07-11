from django.contrib import admin
from .models import EverydayCategory, Pictogram, Person, PatientCaregiverRelationship, PatientPictogram


class PictogramInline(admin.TabularInline):
    model = Pictogram
    extra = 0
    fields = ['name', 'is_active', 'is_default', 'image', 'audio']
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
    list_display = ['name', 'category', 'is_default', 'is_active', 'created_by', 'created_at']
    search_fields = ['name', 'description', 'category__name', 'created_by__username']
    list_filter = ['is_default', 'is_active', 'category', 'created_at', 'created_by']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'category', 'description', 'is_active', 'is_default')
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


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ['name', 'cpf', 'get_person_types', 'email', 'phone', 'profession', 'cid', 'is_active', 'created_at']
    search_fields = ['name', 'cpf', 'email', 'phone', 'profession', 'cid']
    list_filter = ['is_patient', 'is_caregiver', 'is_active', 'created_at', 'created_by']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Dados Básicos', {
            'fields': ('name', 'cpf', 'email', 'phone', 'profession', 'cid')
        }),
        ('Endereço', {
            'fields': ('postal_code', 'state', 'city', 'district', 'street', 'number', 'complement'),
            'classes': ('collapse',)
        }),
        ('Tipo de Pessoa', {
            'fields': ('is_patient', 'is_caregiver', 'is_active')
        }),
        ('Informações do Paciente', {
            'fields': ('colors', 'sounds', 'smells', 'hobbies'),
            'classes': ('collapse',),
            'description': 'Campos específicos para pacientes'
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_person_types(self, obj):
        """Mostra os tipos de pessoa de forma mais clara na listagem"""
        types = []
        if obj.is_patient:
            types.append("👤 Paciente")
        if obj.is_caregiver:
            types.append("🤝 Cuidador")
        
        return " | ".join(types) if types else "❌ Sem tipo"
    
    get_person_types.short_description = "Tipos"
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Otimiza as consultas incluindo o usuário criador"""
        return super().get_queryset(request).select_related('created_by')


@admin.register(PatientCaregiverRelationship)
class PatientCaregiverRelationshipAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'caregiver', 'relationship_type', 'start_date', 
        'is_active', 'created_by', 'created_at'
    ]
    search_fields = [
        'patient__name', 'patient__cpf', 
        'caregiver__name', 'caregiver__cpf'
    ]
    list_filter = [
        'relationship_type', 'is_active', 'start_date', 
        'created_at', 'created_by'
    ]
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['-start_date', 'patient__name']
    
    fieldsets = (
        ('Relacionamento', {
            'fields': ('patient', 'caregiver', 'relationship_type', 'start_date')
        }),
        ('Informações Adicionais', {
            'fields': ('notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at', 'inactivated_at', 'inactivated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Otimiza as consultas incluindo relacionamentos"""
        return super().get_queryset(request).select_related(
            'patient', 'caregiver', 'created_by', 'inactivated_by'
        )


@admin.register(PatientPictogram)
class PatientPictogramAdmin(admin.ModelAdmin):
    list_display = [
        'patient', 'pictogram', 'is_active', 'created_by', 'created_at'
    ]
    search_fields = [
        'patient__name', 'patient__cpf', 
        'pictogram__name', 'pictogram__category__name'
    ]
    list_filter = [
        'is_active', 'created_at', 'created_by',
        'pictogram__category', 'pictogram__is_default'
    ]
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    ordering = ['-created_at', 'patient__name']
    
    fieldsets = (
        ('Vinculação', {
            'fields': ('patient', 'pictogram', 'is_active')
        }),
        ('Informações do Sistema', {
            'fields': ('created_by', 'created_at', 'updated_at', 'inactivated_at', 'inactivated_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é um novo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Otimiza as consultas incluindo relacionamentos"""
        return super().get_queryset(request).select_related(
            'patient', 'pictogram', 'pictogram__category', 'created_by', 'inactivated_by'
        )

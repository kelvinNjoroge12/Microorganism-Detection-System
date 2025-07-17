from django.contrib import admin
from .models import Prediction, ModelVersion
from .model_service import AIClassifier

classifier = AIClassifier()

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('get_user_username', 'microorganism', 'harmful', 'food_source', 'confidence', 'date_created', 'is_verified')
    list_filter = ('harmful', 'microorganism', 'food_source', 'confidence')
    search_fields = ('user__username', 'microorganism', 'food_source')  # Removed user__email
    readonly_fields = ('date_created', 'verified_by', 'verification_date')
    ordering = ('-date_created',)
    autocomplete_fields = ('user', 'verified_by')

    fieldsets = (
        ('Prediction Details', {
            'fields': ('user', 'image', 'microorganism', 'harmful', 'food_source', 'confidence')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verification_date', 'verification_notes'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk and obj.verified_by:
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)

    @admin.display(boolean=True)
    def is_verified(self, obj):
        return obj.verified_by is not None

    def get_user_username(self, obj):
        return obj.user.username
    get_user_username.short_description = 'User'
    get_user_username.admin_order_field = 'user__username'

@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ('version', 'get_uploaded_by_username', 'uploaded_at', 'is_active', 'accuracy')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('version', 'release_notes')
    readonly_fields = ('uploaded_at', 'uploaded_by')
    ordering = ('-uploaded_at',)
    actions = ['reload_classifier']

    fieldsets = (
        ('Version Info', {
            'fields': ('version', 'model_file', 'encoder_file', 'release_notes', 'accuracy')
        }),
        ('Activation', {
            'fields': ('is_active',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        if obj.is_active:
            ModelVersion.objects.exclude(pk=obj.pk).update(is_active=False)
        super().save_model(request, obj, form, change)

        if obj.is_active:
            if classifier.load_model():  # Changed from reload_model to load_model
                self.message_user(request, "Model activated and loaded successfully")
            else:
                self.message_user(request, "Model activated but failed to load", level='ERROR')

    def reload_classifier(self, request, queryset=None):  # Made queryset optional
        if classifier.load_model():  # Changed from reload_model to load_model
            self.message_user(request, "Classifier reloaded successfully")
        else:
            self.message_user(request, "Failed to reload classifier", level='ERROR')
    reload_classifier.short_description = "Reload classifier with active model"

    def get_uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else None
    get_uploaded_by_username.short_description = 'Uploaded By'
    get_uploaded_by_username.admin_order_field = 'uploaded_by__username'
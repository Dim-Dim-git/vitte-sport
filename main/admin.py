from django.contrib import admin
from .models import Sport, News, UserProfile, Training, Feedback, TrainingRecord, Gallery, Tournament, TournamentParticipant, Achievement, TrainingNote, TrainingBlock


admin.site.register(Sport)
admin.site.register(News)
admin.site.register(UserProfile)
admin.site.register(Training)

# Отметить обращения как прочитанные
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)
mark_as_read.short_description = 'Отметить как прочитанное'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'created', 'is_read')
    list_filter   = ('is_read',)
    search_fields = ('name', 'email')
    actions       = [mark_as_read]

# Отметить явку студентов
def mark_attended(modeladmin, request, queryset):
    queryset.update(attended=True)
mark_attended.short_description = 'Отметить явку'

@admin.register(TrainingRecord)
class TrainingRecordAdmin(admin.ModelAdmin):
    list_display  = ('user', 'training', 'created', 'attended')
    list_filter   = ('attended', 'training__sport')
    search_fields = ('user__username',)
    actions       = [mark_attended]

admin.site.register(Gallery)
admin.site.register(Tournament)
admin.site.register(TournamentParticipant)
admin.site.register(Achievement)
admin.site.register(TrainingNote)

@admin.register(TrainingBlock)
class TrainingBlockAdmin(admin.ModelAdmin):
    list_display  = ('title', 'sport', 'kind', 'duration_min')
    list_filter   = ('kind', 'sport')
    search_fields = ('title', 'equipment', 'description')
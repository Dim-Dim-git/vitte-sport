from django.contrib import admin
from .models import Sport, News, UserProfile, Training, Feedback, TrainingRecord, Gallery, Tournament, TournamentParticipant


admin.site.register(Sport)
admin.site.register(News)
admin.site.register(UserProfile)
admin.site.register(Training)
admin.site.register(Feedback)
admin.site.register(TrainingRecord)
admin.site.register(Gallery)
admin.site.register(Tournament)
admin.site.register(TournamentParticipant)

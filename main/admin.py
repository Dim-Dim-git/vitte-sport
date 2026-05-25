from django.contrib import admin
from .models import Sport, News, UserProfile

admin.site.register(Sport)
admin.site.register(News)
admin.site.register(UserProfile)
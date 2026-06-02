"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', views.profile, name='profile'),
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('sports/', views.sports, name='sports'),
    path('news/', views.news, name='news'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('ratings/', views.ratings, name='ratings'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('sports/<int:pk>/', views.sport_detail, name='sport_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/trainings/', views.profile_trainings, name='profile_trainings'),
    path('profile/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('profile/coach/<int:pk>/', views.mark_attendance, name='mark_attendance'),
    path('schedule/register/<int:pk>/', views.training_register, name='training_register'),
    path('admin_panel/users/', views.admin_panel_users, name='admin_panel_users'),
    path('admin_panel/feedback/', views.admin_panel_feedback, name='admin_panel_feedback'),
    path('admin_panel/news/', views.admin_panel_news, name='admin_panel_news'),
    path('admin_panel/news/delete/<int:pk>/', views.admin_panel_news_delete, name='admin_panel_news_delete'),
    path('admin_panel/schedule/', views.admin_panel_schedule, name='admin_panel_schedule'),
    path('admin_panel/schedule/delete/<int:pk>/', views.admin_panel_schedule_delete, name='admin_panel_schedule_delete'),
    path('admin_panel/', views.admin_panel, name='admin_panel'),
    path('admin_panel/gallery/', views.admin_panel_gallery, name='admin_panel_gallery'),
    path('tournaments/', views.tournaments, name='tournaments'),
    path('tournaments/register/<int:pk>/', views.tournament_register, name='tournament_register'),
    path('profile/coach/achievement/add/', views.coach_achievement_add, name='coach_achievement_add'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

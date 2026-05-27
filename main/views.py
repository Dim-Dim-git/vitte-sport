from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Sport, News, UserProfile, Training

# Главная страница
def index(request):
    sports = Sport.objects.all()
    news   = News.objects.all()
    return render(request, 'index.html', {
        'sports': sports,
        'news':   news,
    })

# Выход из системы 
def logout_view(request):
    logout(request)
    return redirect('/')

# Регистрация нового пользователя
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Личный кабинет (доступен только авторизованным пользователям)
@login_required
def profile(request):
    return render(request, 'profile/index.html', {
        'user': request.user
    })

# Страница расписания    
def schedule(request):
    trainings = Training.objects.all()
    days = Training.DAYS
    return render(request, 'schedule.html', {
        'trainings': trainings,
        'days': days,
    })

# Страница секци    
def sports(request):
    sports = Sport.objects.all()
    return render(request, 'sports.html', {
        'sports': sports
    })

# Страница новостей    
def news(request):
    news = News.objects.all()
    return render(request, 'news.html', {
        'news': news
    })

# Страница контактов
def contacts(request):
    return render(request, 'contacts.html')

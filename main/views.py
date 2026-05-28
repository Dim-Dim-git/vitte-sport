from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .models import Sport, News, UserProfile, Training, Feedback, TrainingRecord, Gallery

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

# Страница контактов с формой обратной связи
def contacts(request):
    success = False
    if request.method == 'POST':
        name    = request.POST.get('name')
        email   = request.POST.get('email')
        message = request.POST.get('message')
        # Сохраняем сообщение в БД
        Feedback.objects.create(name=name, email=email, message=message)
        success = True
    return render(request, 'contacts.html', {'success': success})

# Страница о портале
def about(request):
    return render(request, 'about.html')

# Страница рейтингов, топ студентов по количеству посещённых тренировок
def ratings(request):
    from django.db.models import Count
    top = TrainingRecord.objects.filter(attended=True)\
        .values('user__username')\
        .annotate(count=Count('id'))\
        .order_by('-count')[:20]
    return render(request, 'ratings.html', {'top': top})

# Детальная страница новости
def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    return render(request, 'news_detail.html', {'item': item})

# Детальная страница секции
def sport_detail(request, pk):
    sport = get_object_or_404(Sport, pk=pk)
    trainings = Training.objects.filter(sport=sport)
    return render(request, 'sport_detail.html', {
        'sport': sport,
        'trainings': trainings
    })

# Страница галереи
def gallery(request):
    photos = Gallery.objects.all()
    return render(request, 'gallery.html', {'photos': photos})

# Редактирование профиля пользователя
@login_required
def profile_edit(request):
    profile = request.user.userprofile
    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.group = request.POST.get('group')
        profile.save()
        return redirect('/profile/')
    return render(request, 'profile/edit.html', {'profile': profile})
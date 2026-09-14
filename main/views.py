import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import HttpResponse
from .models import Sport, News, UserProfile, Training, Feedback, TrainingRecord, Gallery, Tournament, TournamentParticipant, Achievement, TrainingNote, TrainingBlock, TrainingProgram, ProgramBlock
from .forms import TrainingBlockForm, TrainingProgramForm, ProgramBlockForm
from .pdf import build_program_pdf

# Главная страница
def index(request):
    sports = Sport.objects.all()
    news   = News.objects.all()
    tournaments = Tournament.objects.filter(status__in=['upcoming', 'open'])[:3]
    return render(request, 'index.html', {
        'sports': sports,
        'news':   news,
        'tournaments': tournaments,
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
    achievements = Achievement.objects.filter(user=request.user)
    return render(request, 'profile/index.html', {
        'user': request.user,
        'achievements': achievements,
    })

# Страница расписания    
def schedule(request):
    trainings = Training.objects.all()
    days = Training.DAYS
    
    # ID тренировок на которые уже записан пользователь
    registered_ids = []
    if request.user.is_authenticated:
        registered_ids = TrainingRecord.objects.filter(
            user=request.user
        ).values_list('training_id', flat=True)    
       
    return render(request, 'schedule.html', {
        'trainings': trainings,
        'days': days,
        'user': request.user,
        'registered_ids': registered_ids
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

# Мои тренировки, список записей пользователя
@login_required
def profile_trainings(request):
    records = TrainingRecord.objects.filter(user=request.user)
    tournament_records = TournamentParticipant.objects.filter(user=request.user)
    return render(request, 'profile/trainings.html', 
        {'records': records,
        'tournament_records': tournament_records,
        })

# Страница тренера, управление тренировками
@login_required
def coach_dashboard(request):
    try:
        profile = request.user.userprofile
        if profile.role != 'coach':
            return redirect('/profile/')
    except:
        return redirect('/profile/')
    
    trainings = Training.objects.all()
    students  = UserProfile.objects.filter(role='student')
    sports    = Sport.objects.all()
    notes     = TrainingNote.objects.filter(coach=request.user).select_related('training')[:10]

    
    return render(request, 'profile/coach.html', {
        'trainings': trainings,
        'students': students,
        'sports': sports,
        'notes': notes,
        })

# Страница отметки явки студентов
@login_required
def mark_attendance(request, pk):
    training = get_object_or_404(Training, pk=pk)
    records = TrainingRecord.objects.filter(training=training)
    
    if request.method == 'POST':
        for record in records:
            attended = request.POST.get(f'attended_{record.pk}')
            record.attended = attended == 'on'
            record.save()
        return redirect('/profile/coach/')
    
    return render(request, 'profile/attendance.html', {
        'training': training,
        'records': records
    })
    
 
    
# Запись студента на тренировку
@login_required
def training_register(request, pk):
    training = get_object_or_404(Training, pk=pk)
    taken = TrainingRecord.objects.filter(training=training).count()
    if taken >= training.capacity:
        messages.error(request, 'Нет свободных мест на эту тренировку.')
        return redirect('/schedule/')
    record, created = TrainingRecord.objects.get_or_create(user=request.user, training=training)
    if created:
        messages.success(request, 'Вы записаны на тренировку.')
    else:
        messages.info(request, 'Вы уже записаны на эту тренировку.')
    
    return redirect('/schedule/')




# Проверка роли администратора портала
def is_portal_admin(user):
    try:
        return user.userprofile.role == 'portal_admin'
    except:
        return False

# Панель администратора - список пользователей
@login_required
def admin_panel_users(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    users = UserProfile.objects.all()
    return render(request, 'admin_panel/users.html', {'users': users})

# Панель администратора - обратная связь
@login_required
def admin_panel_feedback(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    feedbacks = Feedback.objects.all()
    return render(request, 'admin_panel/feedback.html', {'feedbacks': feedbacks})

# Панель администратора - управление новостями
@login_required
def admin_panel_news(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    if request.method == 'POST':
        title   = request.POST.get('title')
        content = request.POST.get('content')
        News.objects.create(title=title, content=content)
        return redirect('/admin_panel/news/')
    news = News.objects.all()
    return render(request, 'admin_panel/news.html', {'news': news})

# Удаление новости
@login_required
def admin_panel_news_delete(request, pk):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    news = get_object_or_404(News, pk=pk)
    news.delete()
    return redirect('/admin_panel/news/')

# Панель администратора - управление расписанием
@login_required
def admin_panel_schedule(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    if request.method == 'POST':
        sport_id   = request.POST.get('sport')
        type_      = request.POST.get('type')
        day        = request.POST.get('day')
        time_start = request.POST.get('time_start')
        time_end   = request.POST.get('time_end')
        location   = request.POST.get('location')
        Training.objects.create(
            sport_id=sport_id, type=type_, day=day,
            time_start=time_start, time_end=time_end, location=location
        )
        return redirect('/admin_panel/schedule/')
    trainings = Training.objects.all()
    sports    = Sport.objects.all()
    return render(request, 'admin_panel/schedule.html', {
        'trainings': trainings,
        'sports': sports,
        'days': Training.DAYS,
        'types': Training.TYPES,
    })

# Удаление тренировки
@login_required
def admin_panel_schedule_delete(request, pk):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    training = get_object_or_404(Training, pk=pk)
    training.delete()
    return redirect('/admin_panel/schedule/')

# Главная панели администратора - редирект на пользователей
@login_required
def admin_panel(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    return redirect('/admin_panel/users/')

# Панель администратора - галерея
@login_required
def admin_panel_gallery(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    photos = Gallery.objects.all()
    return render(request, 'admin_panel/gallery.html', {'photos': photos, 'sports': Sport.objects.all()})

# Страница со списком турниров
def tournaments(request):
    items = Tournament.objects.all()
    # ID турниров на которые уже записан пользователь
    registered_ids = []
    if request.user.is_authenticated:
        registered_ids = TournamentParticipant.objects.filter(
            user=request.user
        ).values_list('tournament_id', flat=True)
    return render(request, 'tournaments.html', {
        'tournaments': items,
        'registered_ids': registered_ids 
        })


# Запись студента на турнир
@login_required
def tournament_register(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    # Проверяем не превышен ли лимит участников
    taken = TournamentParticipant.objects.filter(tournament=tournament).count()
    if taken >= tournament.max_participants:
        return redirect('/tournaments/')
    TournamentParticipant.objects.get_or_create(user=request.user, tournament=tournament)
    return redirect('/tournaments/')


# Тренер добавляет достижение студенту
@login_required
def coach_achievement_add(request):
    try:
        if request.user.userprofile.role != 'coach':
            return redirect('/profile/')
    except:
        return redirect('/profile/')

    if request.method == 'POST':
        user_id  = request.POST.get('user_id')
        sport_id = request.POST.get('sport_id')
        title    = request.POST.get('title')
        date     = request.POST.get('date')
        Achievement.objects.create(user_id=user_id, sport_id=sport_id, title=title, date=date)

    return redirect('/profile/coach/')


# Экспорт отчёта по посещаемости в xlsx
@login_required
def export_attendance_xlsx(request):
    try:
        if request.user.userprofile.role != 'coach':
            return redirect('/profile/')
    except:
        return redirect('/profile/')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Посещаемость'

    # Заголовки
    ws.append(['Студент', 'Тренировка', 'Вид спорта', 'День', 'Время', 'Явился'])

    records = TrainingRecord.objects.all().select_related('user', 'training', 'training__sport')
    for r in records:
        ws.append([
            r.user.username,
            str(r.training),
            r.training.sport.name,
            r.training.get_day_display(),
            str(r.training.time_start),
            'Да' if r.attended else 'Нет',
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="attendance.xlsx"'
    wb.save(response)
    return response

# Страница достижений студента
@login_required
def profile_achievements(request):
    achievements = Achievement.objects.filter(user=request.user)
    return render(request, 'profile/achievements.html', {'achievements': achievements})

# Список студентов для тренера
@login_required
def coach_students(request):
    try:
        if request.user.userprofile.role != 'coach':
            return redirect('/profile/')
    except:
        return redirect('/profile/')
    students = UserProfile.objects.filter(role='student')
    return render(request, 'profile/students.html', {'students': students})


# Тренер добавляет заметку к тренировке
@login_required
def coach_note_add(request):
    try:
        if request.user.userprofile.role != 'coach':
            return redirect('/profile/')
    except:
        return redirect('/profile/')

    if request.method == 'POST':
        training_id = request.POST.get('training_id')
        text        = request.POST.get('text')
        TrainingNote.objects.create(training_id=training_id, coach=request.user, text=text)

    return redirect('/profile/coach/')


# Добавляем новое фото в галерею
@login_required
def admin_panel_gallery_add(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    if request.method == 'POST' and request.FILES.get('image'):
        Gallery.objects.create(
            title=request.POST.get('title'),
            sport_id=request.POST.get('sport'),
            image=request.FILES['image'],
        )
    return redirect('/admin_panel/gallery/')



# Удаляем фото из галереи по его id
@login_required
def admin_panel_gallery_delete(request, pk):
    
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    
    get_object_or_404(Gallery, pk=pk).delete()
    return redirect('/admin_panel/gallery/')


# Добавить пользователя в админке
@login_required
def admin_panel_users_add(request):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    if request.method == 'POST':
        from django.contrib.auth.models import User
        username = request.POST.get('username')
        password = request.POST.get('password')
        role     = request.POST.get('role')
        user = User.objects.create_user(username=username, password=password)
        UserProfile.objects.create(user=user, role=role)
    return redirect('/admin_panel/users/')

# Удалить пользователя в админке
@login_required
def admin_panel_users_delete(request, pk):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    from django.contrib.auth.models import User
    get_object_or_404(User, pk=pk).delete()
    return redirect('/admin_panel/users/')

# Смена роли 
@login_required
def admin_panel_users_role(request, pk):
    if not is_portal_admin(request.user):
        return redirect('/profile/')
    if request.method == 'POST':
        profile = get_object_or_404(UserProfile, pk=pk)
        profile.role = request.POST.get('role')
        profile.save()
    return redirect('/admin_panel/users/')


# Библиотека блоков занятий доступна тренеру и администратору портала
@login_required
def coach_blocks(request):
    role = getattr(request.user.userprofile, 'role', None)
    if role not in ('coach', 'portal_admin'):
        return redirect('/profile/')

    blocks = TrainingBlock.objects.select_related('sport')

    # Фильтры из строки запроса
    sport_id = request.GET.get('sport', '')
    kind     = request.GET.get('kind', '')
    if sport_id.isdigit():
        blocks = blocks.filter(sport_id=sport_id)
    if kind:
        blocks = blocks.filter(kind=kind)

    return render(request, 'profile/blocks.html', {
        'blocks': blocks,
        'sports': Sport.objects.all(),
        'kinds': TrainingBlock.KINDS,
        'selected_sport': sport_id,
        'selected_kind': kind,
    })
    
    
# Создание и редактирование блока занятия
@login_required
def block_edit(request, pk=None):
    role = getattr(request.user.userprofile, 'role', None)
    if role not in ('coach', 'portal_admin'):
        return redirect('/profile/')

    block = get_object_or_404(TrainingBlock, pk=pk) if pk else None

    if request.method == 'POST':
        form = TrainingBlockForm(request.POST, instance=block)
        if form.is_valid():
            form.save()
            return redirect('/profile/coach/blocks/')
    else:
        form = TrainingBlockForm(instance=block)

    return render(request, 'profile/block_form.html', {
        'form': form,
        'training_block': block,
    })



# Удаление блока занятия
@login_required
def block_delete(request, pk):
    role = getattr(request.user.userprofile, 'role', None)
    if role in ('coach', 'portal_admin') and request.method == 'POST':
        TrainingBlock.objects.filter(pk=pk).delete()
    return redirect('/profile/coach/blocks/')


# Список программ тренировок в кабинете тренера
@login_required
def coach_programs(request):
    role = getattr(request.user.userprofile, 'role', None)
    if role not in ('coach', 'portal_admin'):
        return redirect('/profile/')

    programs = TrainingProgram.objects.select_related('sport')
    return render(request, 'profile/programs.html', {'programs': programs})


# Создание и редактирование программы
@login_required
def program_edit(request, pk=None):
    role = getattr(request.user.userprofile, 'role', None)
    if role not in ('coach', 'portal_admin'):
        return redirect('/profile/')

    program = get_object_or_404(TrainingProgram, pk=pk) if pk else None

    if request.method == 'POST':
        form = TrainingProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            return redirect(f'/profile/coach/programs/{program.pk}/')
    else:
        form = TrainingProgramForm(instance=program)

    return render(request, 'profile/program_form.html', {
        'form': form,
        'training_program': program,
    })


# Удаление программы
@login_required
def program_delete(request, pk):
    role = getattr(request.user.userprofile, 'role', None)
    if role in ('coach', 'portal_admin') and request.method == 'POST':
        TrainingProgram.objects.filter(pk=pk).delete()
    return redirect('/profile/coach/programs/')

# Состав программы: блоки по занятиям и форма добавления
@login_required
def program_items(request, pk):
    role = getattr(request.user.userprofile, 'role', None)
    if role not in ('coach', 'portal_admin'):
        return redirect('/profile/')

    program = get_object_or_404(TrainingProgram, pk=pk)

    if request.method == 'POST':
        # Правка номеров или удаление: строка списка присылает item_id
        item_id = request.POST.get('item_id')
        if item_id:
            item = get_object_or_404(ProgramBlock, pk=item_id, program=program)
            if 'delete' in request.POST:
                item.delete()
            else:
                session = request.POST.get('session', '')
                order   = request.POST.get('order', '')
                if session.isdigit() and order.isdigit():
                    item.session = int(session)
                    item.order   = int(order)
                    item.save()
            return redirect(f'/profile/coach/programs/{program.pk}/')
        form = ProgramBlockForm(request.POST, program=program)
        if form.is_valid():
            item = form.save(commit=False)
            item.program = program
            item.save()
            return redirect(f'/profile/coach/programs/{program.pk}/')
    else:
        form = ProgramBlockForm(program=program)

    # Группируем блоки по номеру занятия
    sessions = {}
    for item in program.items.select_related('block'):
        sessions.setdefault(item.session, []).append(item)

    return render(request, 'profile/program_items.html', {
        'program': program,
        'sessions': sorted(sessions.items()),
        'form': form,
    })

def sport_detail(request, pk):
    sport = get_object_or_404(Sport, pk=pk)
    trainings = Training.objects.filter(sport=sport)
    programs = TrainingProgram.objects.filter(sport=sport)
    return render(request, 'sport_detail.html', {
        'sport': sport,
        'trainings': trainings,
        'programs': programs
    })

# Публичная страница программы тренировок
def program_detail(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)

    # Группируем блоки по номеру занятия
    sessions = {}
    for item in program.items.select_related('block'):
        sessions.setdefault(item.session, []).append(item)

    return render(request, 'program_detail.html', {
        'program': program,
        'sessions': sorted(sessions.items()),
    })

# Выгрузка программы тренировок в PDF
def program_pdf(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk)

    sessions = {}
    for item in program.items.select_related('block'):
        sessions.setdefault(item.session, []).append(item)

    data = build_program_pdf(program, sorted(sessions.items()))

    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="program_{program.pk}.pdf"'
    return response
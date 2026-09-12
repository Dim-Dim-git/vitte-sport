from django.db import models
from django.contrib.auth.models import User




class Sport(models.Model):
    name        = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name        = 'Вид спорта'
        verbose_name_plural = 'Виды спорта'

    def __str__(self):
        return self.name
    
    
    
class News(models.Model):
    title   = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name        = 'Новость'
        verbose_name_plural = 'Новости'
        ordering            = ['-created']

    def __str__(self):
        return self.title
    
    
    
class UserProfile(models.Model):
    ROLES = [
        ('student', 'Студент'),
        ('coach',   'Тренер'),
        ('portal_admin', 'Администратор портала'),
    ]
    user  = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    role  = models.CharField(max_length=20, choices=ROLES, default='student', verbose_name='Роль')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    group = models.CharField(max_length=20, blank=True, verbose_name='Учебная группа')

    class Meta:
        verbose_name        = 'Профиль'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'
    
class Training(models.Model):
    DAYS = [
        ('mon', 'Понедельник'),
        ('tue', 'Вторник'),
        ('wed', 'Среда'),
        ('thu', 'Четверг'),
        ('fri', 'Пятница'),
        ('sat', 'Суббота'),
        ('sun', 'Воскресенье'),
    ]
    TYPES = [
        ('home',    'Индивидуальная'),
        ('gym',     'Тренажёрный зал'),
        ('section', 'Секция'),
        ('workout', 'Воркаут'),
    ]

    sport      = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name='Вид спорта')
    type       = models.CharField(max_length=20, choices=TYPES, default='section', verbose_name='Тип')
    day        = models.CharField(max_length=3, choices=DAYS, verbose_name='День недели')
    time_start = models.TimeField(verbose_name='Начало')
    time_end   = models.TimeField(verbose_name='Конец')
    location   = models.CharField(max_length=200, blank=True, verbose_name='Место')
    capacity   = models.PositiveIntegerField(default=20, verbose_name='Мест всего')
    notes      = models.TextField(blank=True, verbose_name='Описание / задание')

    class Meta:
        verbose_name        = 'Тренировка'
        verbose_name_plural = 'Расписание'
        ordering            = ['day', 'time_start']

    def __str__(self):
        return f'{self.get_type_display()} — {self.sport} — {self.get_day_display()}'
    
# Обратная связь, сообщения от пользователей портала
class Feedback(models.Model):
    name    = models.CharField(max_length=100, verbose_name='Имя')
    email   = models.EmailField(verbose_name='Email')
    message = models.TextField(verbose_name='Сообщение')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')

    class Meta:
        verbose_name        = 'Обращение'
        verbose_name_plural = 'Обратная связь'
        ordering            = ['-created']

    def __str__(self):
        return f'{self.name} — {self.email}'
    
# Запись студента на тренировку
class TrainingRecord(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Студент')
    training = models.ForeignKey(Training, on_delete=models.CASCADE, verbose_name='Тренировка')
    created  = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    attended = models.BooleanField(default=False, verbose_name='Явился')

    class Meta:
        verbose_name        = 'Запись на тренировку'
        verbose_name_plural = 'Записи на тренировки'
        unique_together     = ('user', 'training')

    def __str__(self):
        return f'{self.user.username} — {self.training}'
    
# Фото с тренировок
class Gallery(models.Model):
    title   = models.CharField(max_length=200, verbose_name='Подпись')
    image = models.URLField(verbose_name='Ссылка на фото')
    sport   = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Вид спорта')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')

    class Meta:
        verbose_name        = 'Фото'
        verbose_name_plural = 'Галерея'
        ordering            = ['-created']

    def __str__(self):
        return self.title
    
# Турниры и соревнования
class Tournament(models.Model):
    # Возможные статусы турнира
    STATUSES = [
        ('upcoming', 'Анонсирован'),
        ('open', 'Идёт регистрация'),
        ('running', 'Проходит'),
        ('finished', 'Завершён'),
        ('cancelled', 'Отменен'),
    ]
    title            = models.CharField(max_length=200, verbose_name='Название')
    sport            = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name='Вид спорта')
    description      = models.TextField(blank=True, verbose_name='Описание')
    date_start       = models.DateField(verbose_name='Дата начала')
    date_end         = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
    location         = models.CharField(max_length=200, blank=True, verbose_name='Место проведения')
    status           = models.CharField(max_length=20, choices=STATUSES, default='upcoming', verbose_name='Статус')
    max_participants = models.PositiveIntegerField(default=32, verbose_name='Макс. участников')
    created          = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name        = 'Турнир'
        verbose_name_plural = 'Турниры'
        ordering            = ['-date_start']

    def __str__(self):
        return f'{self.title} ({self.sport})'


# Заявки студентов на турниры
class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name='Турнир')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Участник')
    # Дата заявки заполняется автоматически
    registered = models.DateTimeField(auto_now_add=True, verbose_name='Дата заявки')

    class Meta:
        verbose_name        = 'Участник турнира'
        verbose_name_plural = 'Участники турниров'
        # Один студент не может записаться на один турнир дважды
        unique_together     = ('tournament', 'user')

    def __str__(self):
        return f'{self.user.username} - {self.tournament.title}'
    

# Достижения студентов, вносит тренер
class Achievement(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Студент')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name='Вид спорта')
    title = models.CharField(max_length=200, verbose_name='Достижение')
    date  = models.DateField(verbose_name='Дата')

    class Meta:
        verbose_name        = 'Достижение'
        verbose_name_plural = 'Достижения'
        ordering            = ['-date']

    def __str__(self):
        return f'{self.user.username} - {self.title}'
    
# Заметки тренера к тренировке
class TrainingNote(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, verbose_name='Тренировка')
    coach    = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Тренер')
    text     = models.TextField(verbose_name='Заметка')
    created  = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name        = 'Заметка тренера'
        verbose_name_plural = 'Заметки тренеров'
        ordering            = ['-created']

    def __str__(self):
        return f'{self.coach.username} - {self.training}'
    
    
# Блок занятия. Элемент, из которого тренер собирает программу тренировок
class TrainingBlock(models.Model):
    KINDS = [
        ('warmup', 'Разминка'),
        ('main',   'Основная часть'),
        ('final',  'Заключительная часть'),
    ]

    title        = models.CharField(max_length=200, verbose_name='Название')
    sport        = models.ForeignKey(Sport, on_delete=models.CASCADE, null=True, blank=True,
                                     related_name='blocks', verbose_name='Вид спорта',
                                     help_text='Оставьте пустым, если блок подходит для любого вида спорта')
    kind         = models.CharField(max_length=20, choices=KINDS, default='main', verbose_name='Тип блока')
    duration_min = models.PositiveIntegerField(default=10, verbose_name='Длительность, мин')
    equipment    = models.CharField(max_length=200, blank=True, verbose_name='Инвентарь')
    description  = models.TextField(verbose_name='Содержание блока')
    scheme       = models.CharField(max_length=200, blank=True, verbose_name='Файл схемы',
                                    help_text='Путь к SVG в статике, например schemes/football-slalom.svg')


    class Meta:
        verbose_name        = 'Блок занятия'
        verbose_name_plural = 'Блоки занятий'
        ordering            = ['sport__name', 'kind', 'title']

    def __str__(self):
        return self.title
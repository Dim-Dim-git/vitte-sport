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
        ('admin',   'Администратор'),
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
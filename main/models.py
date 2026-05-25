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
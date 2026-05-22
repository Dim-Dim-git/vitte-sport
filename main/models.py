from django.db import models


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
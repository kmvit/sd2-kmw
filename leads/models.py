# -*- coding: utf-8 -*-
"""Заявки с сайта.

Письмо директору вынесено в отдельную модель не для красоты: на сайте обещано,
что его читает только директор и что писать можно анонимно. Отдельная модель
позволяет закрыть доступ правами и не смешивать такие сообщения с общим
списком заявок отдела продаж.
"""
from django.db import models


class Lead(models.Model):
    """Заявка на расчёт из формы «Пришлите объём»."""

    NEW = 'new'
    IN_WORK = 'work'
    DONE = 'done'
    SPAM = 'spam'
    STATUSES = [(NEW, 'Новая'), (IN_WORK, 'В работе'),
                (DONE, 'Обработана'), (SPAM, 'Спам')]

    name = models.CharField('Имя', max_length=150)
    phone = models.CharField('Телефон', max_length=40)
    product = models.CharField('Что нужно', max_length=120, blank=True)
    details = models.CharField('Объём и адрес', max_length=300, blank=True)
    page = models.CharField('Страница', max_length=200, blank=True,
                            help_text='С какой страницы отправлена заявка')
    utm = models.CharField('Метки кампании', max_length=300, blank=True)
    status = models.CharField('Статус', max_length=10, choices=STATUSES, default=NEW)
    comment = models.TextField('Комментарий менеджера', blank=True)
    created = models.DateTimeField('Когда пришла', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created']

    def __str__(self):
        return f'{self.name}, {self.phone}'


class DirectorMessage(models.Model):
    """Обращение к директору — приходит на его личную почту.

    Контакты необязательны: на сайте прямо сказано, что написать можно
    анонимно. Поэтому ни IP, ни другие следы здесь не сохраняются.
    """

    message = models.TextField('Текст обращения')
    contact = models.CharField('Как связаться', max_length=200, blank=True,
                               help_text='Телефон или почта, если оставили')
    created = models.DateTimeField('Когда пришло', auto_now_add=True)
    read = models.BooleanField('Прочитано', default=False)

    class Meta:
        verbose_name = 'Письмо директору'
        verbose_name_plural = 'Письма директору'
        ordering = ['-created']

    def __str__(self):
        return f'Обращение от {self.created:%d.%m.%Y}'

# -*- coding: utf-8 -*-
"""Справочники, которые не относятся к продукции: люди, документы, объекты.

Всё это живёт отдельно от страниц: сотрудники и сертификаты показываются
в нескольких местах сайта, а править их удобнее одним списком.
"""
from django.db import models

from core.models import Ordered


class TeamMember(Ordered):
    """Сотрудник на странице контактов.

    Состав и должности совпадают с блоком «Команда» на сайте группы —
    руководство у завода и группы общее.
    """

    name = models.CharField('Имя и фамилия', max_length=150)
    full_name = models.CharField('Имя и отчество', max_length=150, blank=True,
                                 help_text='Строка под именем, например «Михаил Алексеевич»')
    position = models.CharField('Должность', max_length=200)
    note = models.CharField('Уточнение', max_length=200, blank=True,
                            help_text='Чем занимается: «бетон, раствор, ЖБИ»')
    photo = models.ImageField('Фото', upload_to='team/', blank=True,
                              help_text='Портрет 3:4. Если пусто — заглушка «фото уточняется»')
    email = models.EmailField('E-mail', blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Команда'

    def __str__(self):
        return f'{self.name} — {self.position}'


class MemberPhone(Ordered):
    """Прямой номер сотрудника: у многих их два-три."""

    member = models.ForeignKey(TeamMember, verbose_name='Сотрудник', on_delete=models.CASCADE,
                              related_name='phones')
    number = models.CharField('Телефон', max_length=40)

    class Meta(Ordered.Meta):
        verbose_name = 'Телефон сотрудника'
        verbose_name_plural = 'Телефоны сотрудников'

    def __str__(self):
        return self.number

    @property
    def link(self):
        """Номер для href="tel:" — без разделителей."""
        import re
        return '+' + re.sub(r'\D', '', self.number)


class Certificate(Ordered):
    """Сертификат соответствия. Скан открывается в новой вкладке.

    Срок действия виден в админке не просто так: сканы со старого сайта
    выданы в 2017–2018 годах и просрочены — их нужно заменить до запуска.
    """

    title = models.CharField('Что сертифицировано', max_length=200)
    gost = models.CharField('ГОСТ', max_length=120, blank=True)
    scan = models.ImageField('Скан', upload_to='certs/')
    thumb = models.ImageField('Миниатюра', upload_to='certs/', blank=True,
                              help_text='Уменьшенная копия для плитки. Пусто — возьмём скан')
    valid_until = models.DateField('Действует до', null=True, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Сертификат'
        verbose_name_plural = 'Сертификаты'

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        from django.utils import timezone
        return bool(self.valid_until and self.valid_until < timezone.localdate())


class Partner(Ordered):
    """Поставщик сырья или производитель оборудования — логотип в сетке."""

    title = models.CharField('Название', max_length=120)
    logo = models.ImageField('Логотип', upload_to='partners/', blank=True)
    caption = models.CharField('Подпись', max_length=120, blank=True,
                               help_text='Что поставляет: «Бетонные заводы». Перенос строки — <br>')

    class Meta(Ordered.Meta):
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'

    def __str__(self):
        return self.title


class ProjectObject(Ordered):
    """Объект, построенный из нашего бетона.

    Фотографий у завода нет, а чужие снимки ставить нельзя — поэтому это
    реестр названий, без карточек и страниц.
    """

    category = models.CharField('Категория', max_length=100,
                                help_text='Торговая недвижимость, жильё, инфраструктура')
    title = models.CharField('Название', max_length=200)
    place = models.CharField('Город', max_length=120, blank=True)
    is_greenhouse = models.BooleanField('Тепличный комплекс', default=False,
                                        help_text='Показывать в блоке тепличных комплексов, '
                                                  'а не в общем реестре объектов')
    text = models.TextField('Описание', blank=True,
                            help_text='Только для тепличных комплексов')

    class Meta(Ordered.Meta):
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'

    def __str__(self):
        return f'{self.title}, {self.place}' if self.place else self.title


class Faq(Ordered):
    """Вопрос и ответ в блоке «Что спрашивают перед заказом»."""

    question = models.CharField('Вопрос', max_length=300)
    answer = models.TextField('Ответ')

    class Meta(Ordered.Meta):
        verbose_name = 'Вопрос и ответ'
        verbose_name_plural = 'Вопросы и ответы'

    def __str__(self):
        return self.question


class TimelineEvent(Ordered):
    """Событие в истории модернизации завода."""

    year = models.CharField('Год', max_length=20)
    title = models.CharField('Что произошло', max_length=200)
    text = models.TextField('Подробнее', blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Событие истории'
        verbose_name_plural = 'История завода'

    def __str__(self):
        return f'{self.year} — {self.title}'


class WorkSchedule(Ordered):
    """Часы работы участка: продажи, производство, отгрузка, карьер."""

    title = models.CharField('Участок', max_length=120)
    weekdays = models.CharField('Понедельник — суббота', max_length=120,
                                help_text='8:00 — 16:30')
    sunday = models.CharField('Воскресенье', max_length=60, blank=True, default='Выходной')
    phone = models.CharField('Телефон', max_length=40, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Режим работы участка'
        verbose_name_plural = 'Режим работы участков'

    def __str__(self):
        return self.title

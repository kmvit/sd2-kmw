# -*- coding: utf-8 -*-
"""Общие данные сайта, страницы и блоки на них.

Набор страниц задан вёрсткой, поэтому в админке их не создают — правят тексты,
заголовки секций и SEO. Структура повторяет проект ГАНИН ГРУПП: там тот же
подход проверен на 14 страницах и теми же администраторами.
"""
import re

from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import strip_tags


class Ordered(models.Model):
    """Сортировка и скрытие — нужны почти каждой записи контента."""

    order = models.PositiveIntegerField('Порядок', default=100,
                                        help_text='Меньше — выше в списке')
    published = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        abstract = True
        ordering = ['order', 'id']


class SiteSettings(models.Model):
    """Телефоны, адрес и прочее, что повторяется на всех страницах.

    Запись всегда одна (pk=1): дублировать настройки нечем, а выбирать
    «активную» администратору не нужно.
    """

    # --- телефоны ---
    phone_main = models.CharField('Телефон отдела продаж', max_length=40,
                                  default='+7 928 821-72-11')
    phone_extra = models.CharField('Второй телефон', max_length=40, blank=True,
                                   default='+7 928 821-72-02')
    phone_note = models.CharField('Подпись под телефоном', max_length=100, blank=True,
                                  default='Отдел продаж · пн–сб')

    # --- адрес и режим работы ---
    address = models.CharField('Адрес', max_length=250,
                               default='Пятигорск, Черкесское шоссе, 2')
    address_full = models.CharField('Адрес полностью', max_length=300, blank=True,
                                    default='357522, Ставропольский край, '
                                            'город Пятигорск, Черкесское шоссе, 2 (промзона)')
    work_hours = models.CharField('Режим работы', max_length=120,
                                  default='пн–сб, 8:00–16:30')

    # --- карта ---
    # координаты завода: подставляются в виджет Яндекс.Карт на главной и в контактах
    map_lat = models.CharField('Широта', max_length=20, default='44.053091')
    map_lon = models.CharField('Долгота', max_length=20, default='42.993845')
    map_zoom = models.PositiveSmallIntegerField('Масштаб карты', default=16)

    # --- реквизиты ---
    company = models.CharField('Название организации', max_length=150,
                               default='ЗАО «Стройдеталь-2»')
    founded_year = models.CharField('Год основания', max_length=10, default='1962')

    # --- заявки ---
    lead_emails = models.CharField(
        'Куда слать заявки', max_length=300, blank=True,
        help_text='Адреса через запятую — на них уходит письмо о каждой заявке')
    director_email = models.EmailField(
        'Личная почта директора', blank=True,
        help_text='Форма «написать директору» уходит только сюда, минуя отдел продаж')

    # --- индексация ---
    # пока сайт живёт на техническом домене, он должен быть закрыт от поисковиков
    noindex = models.BooleanField(
        'Закрыть сайт от индексации', default=True,
        help_text='Включено — robots.txt запрещает обход, в страницах стоит noindex. '
                  'Снять в день переезда на рабочий домен')
    metrika_id = models.CharField('Номер счётчика Яндекс.Метрики', max_length=20, blank=True,
                                  help_text='Пусто — счётчик не подключается')

    # --- цены ---
    show_prices = models.BooleanField(
        'Показывать цены', default=True,
        help_text='Выключено — вместо всех цен на сайте будет «по запросу». '
                  'У позиции цену можно убрать и по отдельности, очистив поле')
    price_note = models.CharField(
        'Приписка к ценам', max_length=200, blank=True,
        default='Цены ориентировочные, зависят от объёма партии',
        help_text='Показывается под таблицами с ценами')

    class Meta:
        verbose_name = 'Общие данные сайта'
        verbose_name_plural = 'Общие данные сайта'

    def __str__(self):
        return 'Общие данные сайта'

    def save(self, *args, **kwargs):
        self.pk = 1                      # всегда одна запись
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def phone_main_link(self):
        """Телефон для href="tel:" — без пробелов, скобок и дефисов."""
        return '+' + re.sub(r'\D', '', self.phone_main)

    @property
    def phone_extra_link(self):
        return '+' + re.sub(r'\D', '', self.phone_extra) if self.phone_extra else ''


class MenuItem(Ordered):
    """Пункт меню. Подпункты («Продукция») задаются ссылкой на родителя."""

    title = models.CharField('Название', max_length=80)
    url_name = models.CharField('Маршрут', max_length=60, blank=True,
                                help_text='Имя URL, например produkciya_beton')
    anchor = models.CharField('Якорь', max_length=40, blank=True,
                              help_text='Если пункт ведёт на блок страницы, например products')
    parent = models.ForeignKey('self', verbose_name='Родительский пункт', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='children')
    in_footer = models.BooleanField('Показывать в подвале', default=False)

    class Meta(Ordered.Meta):
        verbose_name = 'Пункт меню'
        verbose_name_plural = 'Меню'

    def __str__(self):
        return f'{self.parent.title} · {self.title}' if self.parent else self.title


class Page(models.Model):
    """Тексты шапки и SEO конкретной страницы.

    Привязка по `slug` = имя маршрута (например produkciya_beton). Страницы
    заводит команда `seed_content`; в админке их правят, но не добавляют —
    набор страниц задан вёрсткой.
    """

    slug = models.CharField('Маршрут', max_length=60, unique=True,
                            help_text='Имя URL — менять не нужно')
    admin_title = models.CharField('Страница', max_length=120,
                                   help_text='Как называется в этом списке')
    h1 = models.CharField('Заголовок на странице (H1)', max_length=250, blank=True,
                          help_text='Можно с разметкой: <br> — перенос, <em> — выделение цветом')
    stamp = models.CharField('Надпись над заголовком', max_length=150, blank=True,
                             help_text='Мелкая подпись со штрихом слева')
    subtitle = models.TextField('Подзаголовок', blank=True)
    body = models.TextField('Основной текст', blank=True,
                            help_text='Для текстовых страниц — политика конфиденциальности. '
                                      'Можно с HTML')
    photo = models.ImageField('Фото в шапке', upload_to='pages/', blank=True,
                              help_text='Фон шапки страницы. Если пусто — берётся фото из вёрстки')
    seo_title = models.CharField('SEO-заголовок (title)', max_length=250, blank=True,
                                 help_text='Если пусто — берётся заголовок страницы')
    seo_description = models.TextField('SEO-описание (description)', blank=True, max_length=400)

    class Meta:
        verbose_name = 'Страница (тексты и SEO)'
        verbose_name_plural = 'Страницы (тексты и SEO)'
        ordering = ['admin_title']

    def __str__(self):
        return self.admin_title

    @property
    def title_tag(self):
        """Заголовок вкладки и поисковой выдачи.

        H1 хранится с разметкой (<br>, <em>) ради дизайна, но в <title> теги
        не рендерятся — поэтому здесь их убираем.
        """
        if self.seo_title:
            return self.seo_title
        text = re.sub(r'<br\s*/?>', ' ', self.h1 or '')
        return re.sub(r'\s+', ' ', strip_tags(text)).strip() or self.admin_title

    def section(self, key):
        """Секция по ключу — чтобы шаблон не падал, если её ещё не завели."""
        return self.sections.filter(key=key, published=True).first()


class Section(Ordered):
    """Заголовок и вводный текст блока страницы.

    Ключ (`key`) совпадает с идентификатором секции в вёрстке — по нему шаблон
    забирает свои тексты. Набор секций задан вёрсткой, а через эту модель
    редактор правит подписи, прячет секцию целиком или меняет их местами.
    """

    page = models.ForeignKey(Page, verbose_name='Страница', on_delete=models.CASCADE,
                             related_name='sections')
    key = models.CharField('Ключ блока', max_length=60,
                           help_text='Совпадает с якорем в вёрстке, например price. Не менять')
    stamp = models.CharField('Надпись над заголовком', max_length=150, blank=True,
                             help_text='Мелкая подпись со штрихом слева, например «Честно про цену»')
    title = models.CharField('Заголовок', max_length=250, blank=True,
                             help_text='Можно с разметкой: <br> — перенос строки')
    lead = models.TextField('Вводный текст', blank=True,
                            help_text='Абзац справа от заголовка')
    note = models.TextField('Примечание под блоком', blank=True,
                            help_text='Мелкий текст после таблицы или сетки')
    photo = models.ImageField('Фото блока', upload_to='sections/', blank=True,
                              help_text='Для блоков со снимком сбоку или на фоне. '
                                        'Пусто — останется фото из вёрстки')
    photo_caption = models.CharField('Подпись к фото', max_length=200, blank=True,
                                     help_text='Синяя плашка в углу снимка')

    class Meta(Ordered.Meta):
        verbose_name = 'Блок страницы'
        verbose_name_plural = 'Блоки страниц'
        constraints = [
            models.UniqueConstraint(fields=['page', 'key'], name='unique_section_key'),
        ]

    def __str__(self):
        return f'{self.page.admin_title} · {self.title or self.key}'


class Card(Ordered):
    """Плитка внутри блока: шаги, преимущества, цифры, объекты.

    Один тип записи закрывает почти все сетки вёрстки — у нас это около
    пятнадцати блоков на одиннадцати страницах. Поля value и sup заполняют
    только плитки-цифры («10–15 %»), у остальных они пустые.
    """

    page = models.ForeignKey(Page, verbose_name='Страница', on_delete=models.CASCADE,
                             related_name='cards')
    section = models.CharField('Блок на странице', max_length=60, default='main',
                               help_text='Ключ блока — тот же, что у заголовка блока')
    icon = models.CharField('Индекс или тег', max_length=40, blank=True,
                            help_text='Короткая подпись сверху: 01, «Шаг 01», «Зона»')
    value = models.CharField('Крупное значение', max_length=30, blank=True,
                             help_text='Для плиток с цифрой, например 10–15 или ×2,5')
    sup = models.CharField('Приписка к значению', max_length=30, blank=True,
                           help_text='Мелкий текст рядом с цифрой: %, литров, часов')
    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст', blank=True)
    photo = models.ImageField('Фото', upload_to='cards/', blank=True,
                              help_text='Для плиток с местом под фото')
    url_name = models.CharField('Маршрут ссылки', max_length=60, blank=True,
                                help_text='Имя URL, если плитка ведёт на страницу')
    anchor = models.CharField('Якорь ссылки', max_length=40, blank=True,
                              help_text='Например request — форма заявки')
    link_label = models.CharField('Подпись ссылки', max_length=100, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Плитка в блоке'
        verbose_name_plural = 'Плитки в блоках'

    def __str__(self):
        return f'{self.page.admin_title} · {self.title}'


class Document(Ordered):
    """Файл для скачивания: реквизиты, договор, документы по охране труда."""

    KIND_CHOICES = [('word', 'Word'), ('pdf', 'PDF'), ('excel', 'Excel'), ('other', 'Файл')]

    title = models.CharField('Название', max_length=200)
    kind = models.CharField('Тип файла', max_length=10, choices=KIND_CHOICES, default='pdf')
    file = models.FileField(
        'Файл', upload_to='documents/', blank=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'rtf'])])
    note = models.CharField('Примечание', max_length=200, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return self.title

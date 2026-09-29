# -*- coding: utf-8 -*-
"""Админка: общие данные сайта, страницы с блоками и плитками."""
from django.contrib import admin

from .models import Card, Document, MenuItem, Page, Section, SiteSettings

admin.site.site_header = 'Сайт завода «Стройдеталь-2»'
admin.site.site_title = 'Стройдеталь-2'
admin.site.index_title = 'Управление сайтом'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Настройки — одна запись, поэтому добавление и удаление закрыты."""

    fieldsets = [
        ('Телефоны', {'fields': ['phone_main', 'phone_extra', 'phone_note']}),
        ('Адрес и режим работы', {'fields': ['address', 'address_full', 'work_hours']}),
        ('Карта', {'fields': ['map_lat', 'map_lon', 'map_zoom'],
                   'description': 'Координаты метки завода на схеме проезда'}),
        ('Реквизиты', {'fields': ['company', 'founded_year']}),
        ('Заявки', {'fields': ['lead_emails', 'director_email']}),
        ('Цены', {'fields': ['show_prices', 'price_note']}),
        ('Поисковые системы', {'fields': ['noindex', 'metrika_id']}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class SectionInline(admin.TabularInline):
    """Заголовки блоков страницы — правятся прямо в карточке страницы."""

    model = Section
    extra = 0
    fields = ['order', 'key', 'stamp', 'title', 'lead', 'note', 'published']
    ordering = ['order']


class CardInline(admin.StackedInline):
    """Плитки страницы. Сгруппированы по ключу блока — он в поле «Блок»."""

    model = Card
    extra = 0
    fields = [('section', 'order', 'published'),
              ('icon', 'value', 'sup'),
              'title', 'text', 'photo',
              ('url_name', 'anchor', 'link_label')]
    ordering = ['section', 'order']


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Страницы заводит команда seed_content — в админке их правят, но не создают."""

    list_display = ['admin_title', 'slug', 'h1']
    search_fields = ['admin_title', 'slug', 'h1']
    inlines = [SectionInline, CardInline]
    fieldsets = [
        (None, {'fields': ['admin_title', 'slug']}),
        ('Шапка страницы', {'fields': ['stamp', 'h1', 'subtitle', 'photo']}),
        ('Текст', {'fields': ['body'],
                   'classes': ['collapse'],
                   'description': 'Нужен только текстовым страницам — например политике'}),
        ('Поисковая выдача', {'fields': ['seo_title', 'seo_description']}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['page', 'key', 'title', 'order', 'published']
    list_filter = ['page', 'published']
    list_editable = ['order', 'published']
    search_fields = ['key', 'title', 'lead']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'page', 'section', 'value', 'order', 'published']
    list_filter = ['page', 'section', 'published']
    list_editable = ['order', 'published']
    search_fields = ['title', 'text']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent', 'url_name', 'order', 'published']
    list_filter = ['published', 'in_footer']
    list_editable = ['order', 'published']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'kind', 'file', 'order', 'published']
    list_filter = ['kind', 'published']
    list_editable = ['order', 'published']

# -*- coding: utf-8 -*-
"""Админка продукции. Каждая таблица сайта — свой список с теми же колонками."""
from django.contrib import admin

from .models import (Aggregate, AsphaltMix, ConcreteGrade, ConcretePump, DeliveryZone,
                     Direction, Mortar, PavingColor, PavingModel, WallBlock,
                     ZhbiGroup, ZhbiItem)

PRICE_FIELDS = ['price', 'price_prefix', 'price_label']


class PricedAdmin(admin.ModelAdmin):
    """Общее для таблиц с ценой: сортировка и скрытие правятся прямо в списке."""

    list_editable = ['order', 'published']
    list_filter = ['published']


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'price_value', 'url_name', 'order', 'published']
    list_editable = ['order', 'published']


@admin.register(ConcreteGrade)
class ConcreteGradeAdmin(PricedAdmin):
    list_display = ['title', 'grade_class', 'water', 'frost', 'price', 'group',
                    'order', 'published']
    list_filter = ['group', 'published']
    search_fields = ['title', 'grade_class']


@admin.register(Mortar)
class MortarAdmin(PricedAdmin):
    list_display = ['title', 'grade', 'mobility', 'price', 'order', 'published']


@admin.register(Aggregate)
class AggregateAdmin(PricedAdmin):
    list_display = ['title', 'fraction', 'gost', 'price', 'group', 'order', 'published']
    list_filter = ['group', 'published']


@admin.register(AsphaltMix)
class AsphaltMixAdmin(PricedAdmin):
    list_display = ['title', 'mix_type', 'grade', 'price', 'order', 'published']


@admin.register(WallBlock)
class WallBlockAdmin(PricedAdmin):
    list_display = ['title', 'grade', 'frost', 'size', 'weight', 'price', 'order', 'published']


@admin.register(PavingModel)
class PavingModelAdmin(PricedAdmin):
    list_display = ['title', 'size', 'thickness', 'per_pack', 'price', 'order', 'published']


@admin.register(PavingColor)
class PavingColorAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_mix', 'order', 'published']
    list_filter = ['is_mix', 'published']
    list_editable = ['order', 'published']


class ZhbiItemInline(admin.TabularInline):
    """Позиции группы — таблица характеристик на странице товара."""

    model = ZhbiItem
    extra = 0
    fields = ['order', 'band', 'title', 'concrete_class', 'frost', 'volume', 'weight',
              'length', 'width', 'height', 'diameter', 'color', 'capacity',
              'price', 'price_label', 'note', 'published']
    ordering = ['order']


@admin.register(ZhbiGroup)
class ZhbiGroupAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'kinds_label', 'item_count', 'order', 'published']
    list_editable = ['order', 'published']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'slug']
    inlines = [ZhbiItemInline]
    fieldsets = [
        (None, {'fields': ['title', 'slug', 'kinds_label', 'photo', ('order', 'published')]}),
        ('Страница товара', {'fields': ['summary', 'description', 'gost', 'note']}),
        ('Поисковая выдача', {'fields': ['seo_title', 'seo_description', 'legacy_url']}),
    ]

    @admin.display(description='Позиций')
    def item_count(self, obj):
        return obj.items.count()


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(PricedAdmin):
    list_display = ['title', 'settlements', 'price', 'order', 'published']


@admin.register(ConcretePump)
class ConcretePumpAdmin(PricedAdmin):
    list_display = ['title', 'reach', 'pad', 'price_text', 'order', 'published']

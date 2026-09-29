# -*- coding: utf-8 -*-
"""Админка заявок.

Сама заявка не редактируется: это то, что прислал клиент. Менеджеру доступны
только статус и комментарий. Письма директору открыты отдельным правом —
на сайте обещано, что их читает только он.
"""
from django.contrib import admin

from .models import DirectorMessage, Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['created', 'name', 'phone', 'product', 'details', 'status']
    list_filter = ['status', 'product', 'created']
    search_fields = ['name', 'phone', 'details']
    list_editable = ['status']
    date_hierarchy = 'created'
    readonly_fields = ['name', 'phone', 'product', 'details', 'page', 'utm', 'created']
    fieldsets = [
        ('Заявка', {'fields': ['created', 'name', 'phone', 'product', 'details']}),
        ('Откуда', {'fields': ['page', 'utm']}),
        ('Работа с заявкой', {'fields': ['status', 'comment']}),
    ]

    def has_add_permission(self, request):
        return False


@admin.register(DirectorMessage)
class DirectorMessageAdmin(admin.ModelAdmin):
    list_display = ['created', 'short', 'contact', 'read']
    list_filter = ['read', 'created']
    list_editable = ['read']
    readonly_fields = ['message', 'contact', 'created']

    @admin.display(description='Обращение')
    def short(self, obj):
        return obj.message[:90] + ('…' if len(obj.message) > 90 else '')

    def has_add_permission(self, request):
        return False

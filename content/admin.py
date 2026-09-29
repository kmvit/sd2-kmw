# -*- coding: utf-8 -*-
"""Админка справочников: команда, сертификаты, объекты, документы."""
from django.contrib import admin
from django.utils.html import format_html

from .models import (Certificate, Faq, MemberPhone, Partner, ProjectObject,
                     TeamMember, TimelineEvent, WorkSchedule)


class MemberPhoneInline(admin.TabularInline):
    model = MemberPhone
    extra = 1
    fields = ['order', 'number']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'has_photo', 'order', 'published']
    list_editable = ['order', 'published']
    inlines = [MemberPhoneInline]

    @admin.display(description='Фото', boolean=True)
    def has_photo(self, obj):
        return bool(obj.photo)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['title', 'gost', 'valid_until', 'expired_mark', 'order', 'published']
    list_editable = ['order', 'published']

    @admin.display(description='Срок')
    def expired_mark(self, obj):
        if not obj.valid_until:
            return '—'
        if obj.is_expired:
            return format_html('<b style="color:#b32">просрочен</b>')
        return 'действует'


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['title', 'caption', 'order', 'published']
    list_editable = ['order', 'published']


@admin.register(ProjectObject)
class ProjectObjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'place', 'is_greenhouse', 'order', 'published']
    list_filter = ['is_greenhouse', 'category', 'published']
    list_editable = ['order', 'published']


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'published']
    list_editable = ['order', 'published']


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'order', 'published']
    list_editable = ['order', 'published']


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['title', 'weekdays', 'sunday', 'phone', 'order', 'published']
    list_editable = ['order', 'published']

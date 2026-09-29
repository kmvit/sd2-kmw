# -*- coding: utf-8 -*-
"""Уведомления о заявках.

Сейчас канал один — почта. Телеграм добавится сюда же: достаточно дописать
функцию отправки и вызвать её в notify_lead, трогать формы и представления
не придётся.
"""
from django.conf import settings
from django.core.mail import send_mail

from core.models import SiteSettings


def _recipients():
    """Адреса получателей из настроек сайта."""
    raw = SiteSettings.get().lead_emails or ''
    return [a.strip() for a in raw.split(',') if a.strip()]


def _send(subject, body, to):
    """Письмо не должно ронять приём заявки: она уже сохранена в базе."""
    if not to:
        return False
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, to, fail_silently=False)
        return True
    except Exception:                      # noqa: BLE001 — почта не обязана работать
        return False


def notify_lead(lead):
    """Письмо о заявке в отдел продаж."""
    body = '\n'.join([
        f'Имя: {lead.name}',
        f'Телефон: {lead.phone}',
        f'Что нужно: {lead.product or "—"}',
        f'Объём и адрес: {lead.details or "—"}',
        f'Страница: {lead.page or "—"}',
        f'Время: {lead.created:%d.%m.%Y %H:%M}',
    ])
    return _send(f'Заявка с сайта: {lead.name}, {lead.phone}', body, _recipients())


def notify_director(message):
    """Обращение уходит только на личную почту директора.

    Отдел продаж и руководители участков его не видят — так обещано на сайте.
    """
    to = SiteSettings.get().director_email
    body = '\n'.join([
        message.message,
        '',
        f'Обратная связь: {message.contact or "не оставлена — обращение анонимное"}',
        f'Время: {message.created:%d.%m.%Y %H:%M}',
    ])
    return _send('Обращение к директору с сайта', body, [to] if to else [])

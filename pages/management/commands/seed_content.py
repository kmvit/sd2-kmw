# -*- coding: utf-8 -*-
"""Перенос контента из вёрстки в базу.

    python manage.py seed_content            дополнить недостающее
    python manage.py seed_content --reset    очистить контент и залить заново

Повторный запуск безопасен: записи ищутся по ключевым полям. Заявки команда
не трогает ни при каком запуске — это данные клиентов, а не контент.
"""
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from catalog.models import Direction
from content.models import Certificate, Faq, Partner, ProjectObject
from core.models import Card, Page, Section, SiteSettings
from pages.seed import directories, home

STATIC = Path(settings.BASE_DIR) / 'static'


def attach(field, rel_path):
    """Положить картинку из вёрстки в media, если её там ещё нет."""
    if not rel_path or field:
        return False
    source = STATIC / rel_path
    if not source.exists():
        return False
    with source.open('rb') as fp:
        field.save(Path(rel_path).name, File(fp), save=False)
    return True


class Command(BaseCommand):
    help = 'Заполняет базу контентом, который сейчас в вёрстке'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help='Очистить контент перед заливкой (заявки не трогает)')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['reset']:
            for model in (Card, Section, Page, Direction, Certificate, Partner,
                          ProjectObject, Faq):
                model.objects.all().delete()
            self.stdout.write('контент очищен')

        SiteSettings.get()
        self.seed_page(home)
        self.seed_directories()
        self.stdout.write(self.style.SUCCESS('готово'))

    # ------------------------------------------------------------------ страницы

    def seed_page(self, module):
        data = dict(module.PAGE)
        photo = data.pop('photo', '')
        page, created = Page.objects.get_or_create(
            slug=data['slug'], defaults={k: v for k, v in data.items() if k != 'slug'})
        if attach(page.photo, photo):
            page.save()
        self.stdout.write(f'страница: {page.admin_title}{" (создана)" if created else ""}')

        for i, (key, stamp, title, lead, note, photo, caption) in enumerate(module.SECTIONS, 1):
            section, _ = Section.objects.get_or_create(
                page=page, key=key,
                defaults={'stamp': stamp, 'title': title, 'lead': lead, 'note': note,
                          'photo_caption': caption, 'order': i * 10})
            if attach(section.photo, photo):
                section.save()
        self.stdout.write(f'  блоков: {page.sections.count()}')

        for key, rows in module.CARDS.items():
            for i, (icon, value, sup, title, text) in enumerate(rows, 1):
                Card.objects.get_or_create(
                    page=page, section=key, title=title,
                    defaults={'icon': icon, 'value': value, 'sup': sup,
                              'text': text, 'order': i * 10})
        self.stdout.write(f'  плиток: {page.cards.count()}')

    # -------------------------------------------------------------- справочники

    def seed_directories(self):
        for i, row in enumerate(directories.DIRECTIONS, 1):
            title, text, chips, price, note, url_name, link, photo = row
            obj, _ = Direction.objects.get_or_create(
                title=title,
                defaults={'text': text, 'chips': chips, 'price_value': price,
                          'price_note': note, 'url_name': url_name, 'link_label': link,
                          'order': i * 10})
            if attach(obj.photo, photo):
                obj.save()
        self.stdout.write(f'направления: {Direction.objects.count()}')

        for i, (title, gost, scan, thumb, until) in enumerate(directories.CERTIFICATES, 1):
            obj, _ = Certificate.objects.get_or_create(
                title=title,
                defaults={'gost': gost, 'valid_until': date.fromisoformat(until),
                          'order': i * 10})
            changed = attach(obj.scan, scan)
            changed |= attach(obj.thumb, thumb)
            if changed:
                obj.save()
        self.stdout.write(f'сертификаты: {Certificate.objects.count()}')

        for i, (title, caption, logo) in enumerate(directories.PARTNERS, 1):
            obj, _ = Partner.objects.get_or_create(
                title=title, defaults={'caption': caption, 'order': i * 10})
            if attach(obj.logo, logo):
                obj.save()
        self.stdout.write(f'партнёры: {Partner.objects.count()}')

        for i, (category, title, place, greenhouse, text) in enumerate(directories.OBJECTS, 1):
            ProjectObject.objects.get_or_create(
                title=title, place=place,
                defaults={'category': category, 'is_greenhouse': greenhouse,
                          'text': text, 'order': i * 10})
        self.stdout.write(f'объекты: {ProjectObject.objects.count()}')

        for i, (question, answer) in enumerate(directories.FAQ, 1):
            Faq.objects.get_or_create(question=question,
                                      defaults={'answer': answer, 'order': i * 10})
        self.stdout.write(f'вопросы: {Faq.objects.count()}')

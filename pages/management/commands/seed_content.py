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

from catalog.models import (Aggregate, AsphaltMix, ConcreteGrade, ConcretePump,
                            DeliveryZone, Direction, Mortar, PavingColor, PavingModel,
                            WallBlock)
from content.models import (Certificate, Faq, MemberPhone, Partner, ProjectObject,
                            TeamMember, TimelineEvent, WorkSchedule)
from core.models import Card, Document, Page, Section, SiteSettings
from catalog.models import ZhbiGroup, ZhbiItem
from pages.seed import catalog as catalog_data
from pages.seed import directories, home, inner
from pages.seed import zhbi_groups

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
                          ProjectObject, Faq, ConcreteGrade, Mortar, Aggregate,
                          AsphaltMix, WallBlock, PavingModel, PavingColor,
                          DeliveryZone, ConcretePump, TeamMember, Document,
                          WorkSchedule, TimelineEvent, ZhbiItem, ZhbiGroup):
                model.objects.all().delete()
            self.stdout.write('контент очищен')

        SiteSettings.get()
        self.seed_page(home)
        for module in inner.ALL_PAGES:
            self.seed_page(type('M', (), module))
        self.seed_directories()
        self.seed_catalog()
        self.seed_zhbi()
        self.seed_team()
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

    # ------------------------------------------------------------------ прайсы

    def seed_catalog(self):
        rows = catalog_data
        for i, (group, title, cls, water, frost, mob, price, label) in enumerate(rows.CONCRETE, 1):
            ConcreteGrade.objects.get_or_create(
                title=title, grade_class=cls,
                defaults={'group': group, 'water': water, 'frost': frost, 'mobility': mob,
                          'price': price, 'price_label': label, 'price_prefix': '',
                          'order': i * 10})
        for i, (group, title, grade, mob, purpose, price, label) in enumerate(rows.MORTARS, 1):
            Mortar.objects.get_or_create(
                title=title, grade=grade,
                defaults={'group': group, 'mobility': mob, 'purpose': purpose, 'price': price,
                          'price_label': label, 'price_prefix': '', 'order': i * 10})
        for i, (group, title, fr, gost, spec, price, label) in enumerate(rows.AGGREGATES, 1):
            Aggregate.objects.get_or_create(
                title=title, fraction=fr,
                defaults={'group': group, 'gost': gost, 'spec': spec, 'price': price,
                          'price_label': label or 'По запросу', 'order': i * 10})
        for i, (title, mtype, grade, purpose, price, label) in enumerate(rows.ASPHALT, 1):
            AsphaltMix.objects.get_or_create(
                title=title,
                defaults={'mix_type': mtype, 'grade': grade, 'purpose': purpose, 'price': price,
                          'price_label': label, 'price_prefix': '', 'order': i * 10})
        for i, (title, grade, frost, cond, size, weight) in enumerate(rows.BLOCKS, 1):
            WallBlock.objects.get_or_create(
                title=title,
                defaults={'grade': grade, 'frost': frost, 'conductivity': cond, 'size': size,
                          'weight': weight, 'price_label': 'Договорная', 'price_prefix': '',
                          'order': i * 10})
        for i, (title, size, thick, pack, pallet) in enumerate(rows.PAVING, 1):
            PavingModel.objects.get_or_create(
                title=title, thickness=thick,
                defaults={'size': size, 'per_pack': pack, 'pallet_weight': pallet,
                          'price_label': 'Договорная', 'price_prefix': '', 'order': i * 10})
        for i, (title, is_mix) in enumerate(rows.COLORS, 1):
            PavingColor.objects.get_or_create(title=title,
                                              defaults={'is_mix': is_mix, 'order': i * 10})
        for i, (title, settlements) in enumerate(rows.ZONES, 1):
            DeliveryZone.objects.get_or_create(
                title=title, defaults={'settlements': settlements, 'price_label': 'По запросу',
                                       'price_prefix': '', 'order': i * 10})
        for i, (title, reach, pad, billing, price_text) in enumerate(rows.PUMPS, 1):
            ConcretePump.objects.get_or_create(
                title=title,
                defaults={'reach': reach, 'pad': pad, 'billing': billing,
                          'price_text': price_text, 'price_label': 'По запросу',
                          'price_prefix': '', 'order': i * 10})
        self.stdout.write(f'прайсы: бетон {ConcreteGrade.objects.count()}, '
                          f'растворы {Mortar.objects.count()}, '
                          f'карьер {Aggregate.objects.count()}, '
                          f'плитка {PavingModel.objects.count()}, '
                          f'блоки {WallBlock.objects.count()}')

    # --------------------------------------------------------- люди и документы

    def seed_team(self):
        for i, (name, full, position, note, phones, email, photo) in enumerate(
                directories.TEAM, 1):
            member, created = TeamMember.objects.get_or_create(
                name=name,
                defaults={'full_name': full, 'position': position, 'note': note,
                          'email': email, 'order': i * 10})
            if attach(member.photo, photo):
                member.save()
            if created:
                for j, number in enumerate(phones, 1):
                    MemberPhone.objects.create(member=member, number=number, order=j * 10)
        self.stdout.write(f'команда: {TeamMember.objects.count()}')

        for i, (title, kind) in enumerate(directories.DOCUMENTS, 1):
            Document.objects.get_or_create(title=title,
                                           defaults={'kind': kind, 'order': i * 10})
        for i, (title, weekdays, sunday, phone) in enumerate(directories.SCHEDULE, 1):
            WorkSchedule.objects.get_or_create(
                title=title, defaults={'weekdays': weekdays, 'sunday': sunday,
                                       'phone': phone, 'order': i * 10})
        for i, (year, title, text) in enumerate(directories.TIMELINE, 1):
            TimelineEvent.objects.get_or_create(
                year=year, defaults={'title': title, 'text': text, 'order': i * 10})
        self.stdout.write(f'документы: {Document.objects.count()}, '
                          f'режим работы: {WorkSchedule.objects.count()}, '
                          f'история: {TimelineEvent.objects.count()}')

    # ---------------------------------------------------------------- ЖБИ

    # У плитки и стеновых блоков позиции лежат в своих справочниках
    # (модели плитки, блоки), поэтому их страницы собираются своим шаблоном.
    CUSTOM_TEMPLATES = {
        'trotuarnaya-plitka': 'zhbi_plitka',
        'stenovye-bloki': 'zhbi_bloki',
    }

    def seed_zhbi(self):
        for i, data in enumerate(zhbi_groups.GROUPS, 1):
            group, created = ZhbiGroup.objects.get_or_create(
                slug=data['slug'],
                defaults={'title': data['title'], 'kinds_label': data['kinds'],
                          'gost': data['gost'], 'description': data['description'],
                          'legacy_url': data['legacy'], 'order': i * 10,
                          'custom_template': self.CUSTOM_TEMPLATES.get(data['slug'], ''),
                          'seo_title': f"{data['title']} в Пятигорске — завод «Стройдеталь-2»",
                          'seo_description': data['description'][:300]})
            if attach(group.photo, data['photo']):
                group.save()
            if created:
                for j, item in enumerate(data['items'], 1):
                    ZhbiItem.objects.create(
                        group=group, order=j * 10,
                        title=item.get('title', ''), band=item.get('band', ''),
                        concrete_class=item.get('concrete_class', ''),
                        frost=item.get('frost', ''), volume=item.get('volume', ''),
                        weight=item.get('weight', ''), length=item.get('length', ''),
                        width=item.get('width', ''), height=item.get('height', ''),
                        diameter=item.get('diameter', ''), color=item.get('color', ''),
                        capacity=item.get('capacity', ''),
                        price_label=item.get('price_label', 'Договорная'),
                        price_prefix='')
        self.stdout.write(f'ЖБИ: групп {ZhbiGroup.objects.count()}, '
                          f'позиций {ZhbiItem.objects.count()}')

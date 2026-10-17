# -*- coding: utf-8 -*-
"""Карта 301-редиректов для переезда со старого сайта.

    python manage.py seed_redirects

Разделы и карточки ЖБИ работают на прежних адресах (pages/legacy.py,
«Адрес на старом сайте» у групп) — переклеивать их поисковику не нужно.
Редиректы закрывают остальное: те же адреса со слешем на конце, снятые
с производства карточки, файлы из индекса и черновые адреса /produkciya/…,
которые были у редизайна на тестовой площадке.
"""
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.utils.encoding import escape_uri_path

from catalog.models import ZhbiGroup
from core.models import Document
from pages.legacy import DRAFT_SECTIONS, DRAFT_ZHBI_PREFIX, SECTIONS

# Карточки, снятые с производства: на старом сайте они уже отдавали 301
# на каталог — сохраняем это поведение, чтобы адреса не начали отдавать 404.
RETIRED = [
    '/zhelezobeton/zhb-lestnichnye-stupeni-LS',
    '/zhelezobeton/pustotnye-plity-perekrytiya-PK-PB',
    '/zhelezobeton/peremychki-bruskovye-PB',
    '/zhelezobeton/kolodcy-kabelnoj-kanalizacii-i-svyazi',
    '/zhelezobeton/LMP-lestnichnye-marshi-lestnicy',
    '/zhelezobeton/vinograd-shpalera-opora',
    '/zhelezobeton/shchelevye-poly-korovnikov-i-svinarnikov',
]

# Файлы старого сайта, которые есть в индексе Яндекса → документ на новом сайте.
# Ведут на файл документа, загруженный в media; договор на старом сайте лежал
# в двух редакциях — обе ведут на действующую.
LEGACY_FILES = {
    '/Бетон СтройДеталь-2.doc': 'Реквизиты ЗАО «Стройдеталь-2»',
    '/Образец  договора поставки продукции ПРЕДОПЛАТА юр лица.doc':
        'Типовой договор поставки продукции',
    '/uploads/article/files/Форма договора поставки (предоплата).doc':
        'Типовой договор поставки продукции',
    '/Приложение к договору Форма заявки.docx': 'Приложение к договору: форма заявки',
    '/uploads/article/files/Приложение к договору Форма Доверенности.docx':
        'Приложение к договору: форма доверенности',
    # та же форма лежит и в корне — на неё ссылаются страницы старого сайта
    '/Приложение к договору Форма Доверенности.docx':
        'Приложение к договору: форма доверенности',
    '/uploads/article/files/anketa_SD2.doc': 'Анкета соискателя',
    '/Сводная_ведомость_резальтатов_проведения.pdf':
        'Сводная ведомость специальной оценки условий труда',
    '/Перечень_рекомендаций_мероприятий.pdf': 'Перечень мероприятий по улучшению условий труда',
    '/zayavlenie-o-politike-bezopastnosti.pdf':
        'Заявление о политике в области промышленной безопасности',
}

# Снято с публикации: пустой новый адрес — Django отдаёт 410 Gone,
# и поисковик убирает файл из индекса, а не ждёт его возвращения.
GONE = [
    '/uploads/article/files/price_alform.xlsx',   # старый прайс, цены на сайте закрыты
]


class Command(BaseCommand):
    help = 'Заводит 301-редиректы для переезда со старого сайта'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        site.domain = 'sd2-kmv.ru'
        site.name = 'Стройдеталь-2'
        site.save()

        catalog = SECTIONS['zhbi']
        live = list(SECTIONS.values())          # эти адреса отдают страницы сами
        pairs = dict(DRAFT_SECTIONS)
        for group in ZhbiGroup.objects.exclude(legacy_url=''):
            live.append(group.legacy_url)
            draft = f'{DRAFT_ZHBI_PREFIX}{group.slug}/'
            pairs[draft] = pairs[draft.rstrip('/')] = group.legacy_url
        for old in RETIRED:
            pairs[old] = catalog
        # тот же адрес со слешем на конце: внешние ссылки бывают и такими
        for path in live + RETIRED:
            pairs.setdefault(path + '/', catalog if path in RETIRED else path)
        for draft in list(DRAFT_SECTIONS):
            pairs.setdefault(draft.rstrip('/'), DRAFT_SECTIONS[draft])
        # прежняя карта вела со старых адресов на черновые — эти строки больше не нужны
        Redirect.objects.filter(site=site, old_path__in=[escape_uri_path(p) for p in live]).delete()
        pairs = {old: new for old, new in pairs.items() if old not in live}
        for old, title in LEGACY_FILES.items():
            doc = Document.objects.filter(title=title).exclude(file='').first()
            if doc:
                pairs[old] = doc.file.url
            else:
                self.stderr.write(f'нет файла у документа «{title}» — {old} пропущен')
        for old in GONE:
            pairs[old] = ''

        created = 0
        for old, new in pairs.items():
            # middleware сравнивает путь в закодированном виде: кириллица и пробелы — через %
            _, made = Redirect.objects.update_or_create(
                site=site, old_path=escape_uri_path(old), defaults={'new_path': new})
            created += made
        self.stdout.write(self.style.SUCCESS(
            f'редиректов: {Redirect.objects.count()} (новых {created})'))

# -*- coding: utf-8 -*-
"""Карта 301-редиректов со старого сайта.

    python manage.py seed_redirects

Без неё переезд обнуляет поисковый трафик: старые адреса собирали его годами,
а страницы каталога ЖБИ — это почти два десятка точек входа. Адреса берутся
из поля «Адрес на старом сайте» у групп изделий плюс список разделов ниже.
"""
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from catalog.models import ZhbiGroup

# старый адрес → новый
SECTIONS = {
    '/cena-betona-s-dostavkoj': '/produkciya/beton/',
    '/ZHB-zavod-ZHBI': '/produkciya/zhbi/',
    '/asfaltobeton': '/produkciya/asfalt/',
    '/karer-shchebnya-i-peska': '/produkciya/inertnye/',
    '/kontakty': '/kontakty/',
}

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


class Command(BaseCommand):
    help = 'Заводит 301-редиректы со старых адресов сайта'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        site.domain = 'sd2-kmv.ru'
        site.name = 'Стройдеталь-2'
        site.save()

        pairs = dict(SECTIONS)
        for group in ZhbiGroup.objects.exclude(legacy_url=''):
            pairs[group.legacy_url] = group.get_absolute_url()
        for old in RETIRED:
            pairs[old] = '/produkciya/zhbi/'

        created = 0
        for old, new in pairs.items():
            _, made = Redirect.objects.get_or_create(
                site=site, old_path=old, defaults={'new_path': new})
            created += made
        self.stdout.write(self.style.SUCCESS(
            f'редиректов: {Redirect.objects.count()} (новых {created})'))

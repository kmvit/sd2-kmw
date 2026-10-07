# -*- coding: utf-8 -*-
"""Общие данные сайта доступны в каждом шаблоне как `site`.

Здесь же собираются адрес сайта для canonical и Open Graph и разметка
организации для поисковиков: она одна на весь сайт и берётся из общих
данных, поэтому меняется вместе с ними из админки.
"""
import json

from django.templatetags.static import static

from .models import SiteSettings


def site(request):
    settings = SiteSettings.get()
    base = f'{request.scheme}://{request.get_host()}'
    return {'site': settings, 'site_base': base,
            'site_schema': organization_schema(settings, base)}


def organization_schema(s, base):
    """Schema.org LocalBusiness: название, телефоны, адрес, точка на карте."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        'name': 'Стройдеталь-2',
        'legalName': s.company,
        'url': base + '/',
        'logo': base + static('apple-touch-icon.png'),
        'image': base + static('img/zavod-30834.jpg'),
        'telephone': [p for p in (s.phone_main, s.phone_extra) if p],
        'address': {'@type': 'PostalAddress',
                    'streetAddress': s.address_full or s.address,
                    'addressCountry': 'RU'},
        'foundingDate': s.founded_year,
    }
    if s.map_lat and s.map_lon:
        data['geo'] = {'@type': 'GeoCoordinates',
                       'latitude': s.map_lat, 'longitude': s.map_lon}
    # «</» внутри <script> закрыл бы тег раньше времени
    return json.dumps(data, ensure_ascii=False).replace('</', '<\\/')

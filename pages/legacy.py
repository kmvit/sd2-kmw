# -*- coding: utf-8 -*-
"""Адреса старого sd2-kmv.ru — сайт работает по ним же.

Страницы, по которым сайт годами собирает поисковый трафик, остаются на прежних
адресах: Яндексу не нужно ничего переклеивать, а в адресах сохраняются слова
из запросов. Карточки ЖБИ живут по `ZhbiGroup.legacy_url`.

Без импорта моделей — модуль используют миграции.
"""

# Разделы: адрес на старом сайте (без слеша на конце, как там и было)
SECTIONS = {
    'beton': '/cena-betona-s-dostavkoj',
    'zhbi': '/ZHB-zavod-ZHBI',
    'asfalt': '/asfaltobeton',
    'karer': '/karer-shchebnya-i-peska',
    'kontakty': '/kontakty',
}

# Адреса, которые были у редизайна на тестовой площадке до возврата старых:
# ссылки на них могли разойтись, поэтому они ведут 301 на рабочие
DRAFT_SECTIONS = {
    '/produkciya/beton/': SECTIONS['beton'],
    '/produkciya/zhbi/': SECTIONS['zhbi'],
    '/produkciya/asfalt/': SECTIONS['asfalt'],
    '/produkciya/inertnye/': SECTIONS['karer'],
    '/kontakty/': SECTIONS['kontakty'],
}
DRAFT_ZHBI_PREFIX = '/produkciya/zhbi/'      # + slug группы + '/'

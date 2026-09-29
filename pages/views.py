# -*- coding: utf-8 -*-
"""Страницы сайта.

Набор страниц задан вёрсткой, поэтому маршруты перечислены здесь таблицей,
а не собираются из базы. Тексты, блоки и справочники представление берёт
из моделей — в админке правится всё, кроме самой структуры страницы.
"""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from catalog.models import (Aggregate, AsphaltMix, ConcreteGrade, ConcretePump,
                            DeliveryZone, Direction, Mortar, PavingColor, PavingModel,
                            WallBlock, ZhbiGroup)
from content.models import (Certificate, Faq, Partner, ProjectObject, TeamMember,
                            TimelineEvent, WorkSchedule)
from core.models import Document, Page, SiteSettings
from leads.forms import DirectorMessageForm, LeadForm
from leads.notify import notify_director, notify_lead

# (адрес, имя маршрута, шаблон, какой пункт меню подсветить)
PAGES = [
    ('',                     'home',         'index',        'products'),
    ('produkciya/beton/',    'beton',        'beton',        'products'),
    ('produkciya/zhbi/',     'zhbi',         'zhbi',         'products'),
    ('produkciya/asfalt/',   'asfalt',       'asfalt',       'products'),
    ('produkciya/inertnye/', 'karer',        'karer',        'karer'),
    ('dostavka/',            'dostavka',     'dostavka',     'dostavka'),
    ('laboratoriya/',        'laboratoriya', 'laboratoriya', 'lab'),
    ('obekty/',              'obekty',       'obekty',       'obekty'),
    ('kontakty/',            'kontakty',     'kontakty',     'kontakty'),
    ('politika/',            'politika',     'politika',     ''),
]

# Что предлагается в поле «Что нужно» формы заявки
PRODUCT_OPTIONS = ['Бетон или раствор', 'ЖБИ, плитка, бордюр',
                   'Асфальтобетон', 'Щебень или песок']

# Какой пункт списка выбран по умолчанию на конкретной странице
PRODUCT_DEFAULT = {
    'zhbi': 'ЖБИ, плитка, бордюр',
    'asfalt': 'Асфальтобетон',
    'karer': 'Щебень или песок',
}


def page_extras(slug):
    """Справочники, нужные конкретной странице."""
    published = {'published': True}
    if slug == 'home':
        return {
            'directions': Direction.objects.filter(**published),
            'certificates': Certificate.objects.filter(**published),
            'partners': Partner.objects.filter(**published),
            'objects': ProjectObject.objects.filter(is_greenhouse=False, **published),
            'faq': Faq.objects.filter(**published),
        }
    if slug == 'beton':
        return {'grades': ConcreteGrade.objects.filter(**published),
                'mortars': Mortar.objects.filter(**published)}
    if slug == 'zhbi':
        return {'groups': ZhbiGroup.objects.filter(**published),
                'blocks': WallBlock.objects.filter(**published),
                'greenhouses': ProjectObject.objects.filter(is_greenhouse=True, **published)}
    if slug == 'asfalt':
        return {'mixes': AsphaltMix.objects.filter(**published)}
    if slug == 'karer':
        return {'aggregates': Aggregate.objects.filter(**published)}
    if slug == 'dostavka':
        return {'zones': DeliveryZone.objects.filter(**published),
                'pumps': ConcretePump.objects.filter(**published)}
    if slug == 'obekty':
        return {'objects': ProjectObject.objects.filter(is_greenhouse=False, **published),
                'greenhouses': ProjectObject.objects.filter(is_greenhouse=True, **published),
                'timeline': TimelineEvent.objects.filter(**published)}
    if slug == 'kontakty':
        return {'team': TeamMember.objects.filter(**published).prefetch_related('phones'),
                'schedule': WorkSchedule.objects.filter(**published),
                'documents': Document.objects.filter(**published),
                'director_form': DirectorMessageForm()}
    return {}


def page_context(request, slug, active):
    """Общий контекст страницы: тексты, блоки, плитки и результат отправки формы."""
    page = Page.objects.filter(slug=slug).prefetch_related('sections', 'cards').first()
    sections, cards = {}, {}
    if page:
        sections = {s.key: s for s in page.sections.all() if s.published}
        for card in page.cards.all():
            if card.published:
                cards.setdefault(card.section, []).append(card)
    ctx = {
        'active': active,
        'page': page,
        'sections': sections,
        'cards': cards,
        'product_options': PRODUCT_OPTIONS,
        'product_default': PRODUCT_DEFAULT.get(slug, PRODUCT_OPTIONS[0]),
        # заявка отправлена — страница открыта после переадресации с формы
        'lead_sent': 'ok' in request.GET,
        'lead_errors': request.session.pop('lead_errors', None),
    }
    ctx.update(page_extras(slug))
    return ctx


def make_page_view(template, active, slug):
    """Фабрика представлений: у всех страниц одна логика, разный шаблон."""
    def view(request):
        return render(request, f'pages/{template}.html', page_context(request, slug, active))
    view.__name__ = f'page_{template}'
    return view


# Колонки таблицы характеристик: поле модели → подпись в шапке.
# Порядок здесь задаёт порядок колонок на странице.
ZHBI_COLUMNS = [
    ('concrete_class', 'Класс бетона'),
    ('frost', 'Морозостойкость'),
    ('volume', 'Объём бетона, м³'),
    ('weight', 'Вес, кг'),
    ('length', 'Длина, мм'),
    ('width', 'Ширина, мм'),
    ('height', 'Высота, мм'),
    ('diameter', 'Диаметр, мм'),
    ('capacity', 'Несущая способность'),
    ('color', 'Цвет'),
]


def zhbi_item(request, slug):
    """Страница группы изделий ЖБИ.

    Набор колонок у групп разный: у колец важен диаметр, у перемычек — несущая
    способность. Поэтому таблица собирается здесь: пустые колонки не выводим,
    чтобы страница не пестрела прочерками.
    """
    group = get_object_or_404(ZhbiGroup, slug=slug, published=True)
    items = list(group.items.filter(published=True))
    columns = [(name, label) for name, label in ZHBI_COLUMNS
               if any(getattr(item, name) for item in items)]
    rows = [{'item': item, 'cells': [getattr(item, name) for name, _ in columns]}
            for item in items]

    ctx = page_context(request, 'zhbi_item', 'products')
    ctx.update({'group': group, 'rows': rows, 'columns': columns,
                'page': group, 'other_groups': ZhbiGroup.objects.filter(published=True)
                                                        .exclude(pk=group.pk)[:8]})
    # у плитки и блоков позиции лежат в своих справочниках
    if group.custom_template == 'zhbi_plitka':
        ctx.update({'models': PavingModel.objects.filter(published=True),
                    'colors': PavingColor.objects.filter(published=True, is_mix=False),
                    'mixes': PavingColor.objects.filter(published=True, is_mix=True)})
    elif group.custom_template == 'zhbi_bloki':
        ctx['blocks'] = WallBlock.objects.filter(published=True)
    return render(request, f'pages/{group.custom_template or "zhbi_item"}.html', ctx)


def _back(request, fragment=''):
    """Вернуться на страницу, с которой отправляли форму."""
    target = (request.POST.get('next') or request.META.get('HTTP_REFERER')
              or reverse('home')).split('#')[0].split('?')[0]
    return HttpResponseRedirect(f'{target}{fragment}')


@require_POST
def lead_create(request):
    """Приём заявки на расчёт."""
    form = LeadForm(request.POST)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.page = (request.POST.get('next') or '')[:200]
        lead.save()
        notify_lead(lead)
        return _back(request, '?ok=1#request')
    request.session['lead_errors'] = [e for errs in form.errors.values() for e in errs]
    return _back(request, '#request')


@require_POST
def director_create(request):
    """Приём обращения к директору — уходит только на его личную почту."""
    form = DirectorMessageForm(request.POST)
    if form.is_valid():
        notify_director(form.save())
        return _back(request, '?ok=1#director')
    request.session['lead_errors'] = [e for errs in form.errors.values() for e in errs]
    return _back(request, '#director')


def robots_txt(request):
    """Пока сайт на техническом домене, обход запрещён целиком."""
    if SiteSettings.get().noindex:
        return HttpResponse('User-agent: *\nDisallow: /\n', content_type='text/plain')
    base = f'{request.scheme}://{request.get_host()}'
    text = ('User-agent: *\n'
            'Disallow: /admin/\n'
            'Disallow: /politika/\n'
            f'Sitemap: {base}/sitemap.xml\n')
    return HttpResponse(text, content_type='text/plain')


def sitemap_xml(request):
    base = f'{request.scheme}://{request.get_host()}'
    locs = [path for path, name, _tpl, _active in PAGES if name != 'politika']
    locs += [f'produkciya/zhbi/{g.slug}/' for g in ZhbiGroup.objects.filter(published=True)]
    items = ''.join(f'  <url><loc>{base}/{loc}</loc></url>\n' for loc in locs)
    return HttpResponse(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + items + '</urlset>\n',
        content_type='application/xml')


def page_not_found(request, exception=None):
    return render(request, 'pages/404.html', {'active': ''}, status=404)

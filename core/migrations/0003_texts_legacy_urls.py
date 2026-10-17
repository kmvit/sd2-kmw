# Сайт вернулся на адреса старого sd2-kmv.ru: ссылки внутри текстов, заведённые
# на черновые /produkciya/…, переводим на рабочие, чтобы не ходить через 301.

from django.db import migrations

from pages.legacy import DRAFT_SECTIONS, DRAFT_ZHBI_PREFIX

FIELDS = {
    'Page': ['subtitle', 'body', 'seo_description'],
    'Section': ['lead', 'note'],
    'Card': ['text'],
}


def to_legacy(apps, schema_editor):
    ZhbiGroup = apps.get_model('catalog', 'ZhbiGroup')
    # сначала карточки — их адреса начинаются с адреса каталога
    pairs = [(f'{DRAFT_ZHBI_PREFIX}{g.slug}/', g.legacy_url)
             for g in ZhbiGroup.objects.exclude(legacy_url='')]
    pairs += [(old, new) for old, new in DRAFT_SECTIONS.items() if old.startswith('/produkciya/')]
    for model_name, fields in FIELDS.items():
        Model = apps.get_model('core', model_name)
        for obj in Model.objects.all():
            changed = []
            for f in fields:
                value = getattr(obj, f) or ''
                new = value
                for old, legacy in pairs:
                    new = new.replace(f'"{old}', f'"{legacy}')
                if new != value:
                    setattr(obj, f, new)
                    changed.append(f)
            if changed:
                obj.save(update_fields=changed)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_section_photo_section_photo_caption'),
        ('catalog', '0004_zhbigroup_legacy_url_help'),
    ]

    operations = [
        migrations.RunPython(to_legacy, migrations.RunPython.noop),
    ]

from django.db import migrations
from django.db.models import Value
from django.db.models.functions import Replace


def update_mixes(apps, schema_editor):
    db = schema_editor.connection.alias
    colors = apps.get_model('catalog', 'PavingColor').objects.using(db)
    colors.filter(is_mix=True, title__in=['Дубай', 'Бомбей']).update(published=False)
    for order, title in enumerate(['Прага', 'Рим', 'Мадрид'], 180):
        colors.update_or_create(
            title=title, is_mix=True,
            defaults={'published': True, 'order': order},
        )
    apps.get_model('catalog', 'ZhbiGroup').objects.using(db).filter(
        slug='trotuarnaya-plitka',
    ).update(seo_description=Replace(
        'seo_description', Value('8 смешений'), Value('9 смешений'),
    ))


class Migration(migrations.Migration):
    dependencies = [('core', '0012_update_alley_curb_colors')]
    operations = [migrations.RunPython(update_mixes, migrations.RunPython.noop)]

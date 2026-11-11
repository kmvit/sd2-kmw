from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations
from django.db.models import Value
from django.db.models.functions import Replace


def refresh_zhbi_catalog(apps, schema_editor):
    db = schema_editor.connection.alias
    pages = apps.get_model('core', 'Page').objects.using(db).filter(slug='zhbi')
    page = pages.first()
    if page:
        photo = Path(settings.BASE_DIR) / 'static/img/zhbi-plitka-sklad.jpg'
        with photo.open('rb') as source:
            page.photo.save(photo.name, File(source), save=False)
        page.save(using=db, update_fields=['photo'])
        pages.update(
            subtitle=Replace('subtitle', Value('19 групп изделий по ГОСТ'), Value('Изделия по ГОСТ')),
            seo_description=Replace('seo_description', Value('293 изделия по ГОСТ'), Value('Изделия по ГОСТ')),
        )

    apps.get_model('core', 'Section').objects.using(db).filter(
        page__slug='zhbi', key='about',
    ).update(lead=Replace('lead', Value('Сегодня это 293 изделия в 19 группах —'),
                          Value('Сегодня выпускаем ЖБИ')))
    apps.get_model('core', 'Card').objects.using(db).filter(
        page__slug='zhbi', section='bar', value='293 вида в 19 группах',
    ).update(title='Изделия', value='по ГОСТ')
    apps.get_model('catalog', 'Direction').objects.using(db).filter(url_name='zhbi').update(
        text=Replace('text', Value('293 вида железобетонных изделий в 19 группах:'),
                     Value('Железобетонные изделия:')),
        chips=Replace('chips', Value('19 групп изделий; '), Value('')),
    )

    groups = apps.get_model('catalog', 'ZhbiGroup').objects.using(db)
    groups.filter(slug__in=('lyuki-kolodcev', 'progony')).update(published=False)
    groups.filter(slug='kolca-kolodcev').update(
        summary=Replace('summary', Value('Плиты днища, перекрытия и люки подберём в комплект.'),
                        Value('Плиты днища и перекрытия подберём в комплект.')),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_texts_legacy_urls'),
        ('catalog', '0005_asphaltmix_gost_fields'),
    ]

    operations = [
        migrations.RunPython(refresh_zhbi_catalog, migrations.RunPython.noop),
    ]

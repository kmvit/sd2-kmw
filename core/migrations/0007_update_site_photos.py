from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


def save_photo(obj, db, source_name, *, filename=None, caption=None):
    if obj is None:
        return
    source_path = Path(settings.BASE_DIR) / 'static' / 'img' / source_name
    with source_path.open('rb') as source:
        obj.photo.save(filename or source_name, File(source), save=False)
    fields = ['photo']
    if caption is not None:
        obj.photo_caption = caption
        fields.append('photo_caption')
    obj.save(using=db, update_fields=fields)


def update_photos(apps, schema_editor):
    db = schema_editor.connection.alias
    pages = apps.get_model('core', 'Page').objects.using(db)
    sections = apps.get_model('core', 'Section').objects.using(db)

    save_photo(pages.filter(slug='dostavka').first(), db, 'sitrak-lineup-beton.jpg',
               filename='sitrak-lineup-dostavka.jpg')
    save_photo(pages.filter(slug='laboratoriya').first(), db, 'laboratoriya-oborudovanie.jpg')
    save_photo(sections.filter(page__slug='home', key='products').first(), db, 'produkciya-zavod.jpg')
    save_photo(sections.filter(page__slug='dostavka', key='control').first(), db, 'dostavka-miksery.jpg')
    save_photo(sections.filter(page__slug='beton', key='water').first(), db, 'beton-operator.jpg',
               caption='Оператор бетонного завода')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_update_beton_hero_photo'),
    ]

    operations = [
        migrations.RunPython(update_photos, migrations.RunPython.noop),
    ]

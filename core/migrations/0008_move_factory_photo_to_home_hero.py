from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


def move_factory_photo(apps, schema_editor):
    db = schema_editor.connection.alias
    page = apps.get_model('core', 'Page').objects.using(db).filter(slug='home').first()
    if page is None:
        return

    photo = Path(settings.BASE_DIR) / 'static/img/produkciya-zavod.jpg'
    with photo.open('rb') as source:
        page.photo.save(photo.name, File(source), save=False)
    page.save(using=db, update_fields=['photo'])

    apps.get_model('core', 'Section').objects.using(db).filter(
        page=page, key='products', photo__startswith='sections/produkciya-zavod',
    ).update(photo='')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_update_site_photos'),
    ]

    operations = [
        migrations.RunPython(move_factory_photo, migrations.RunPython.noop),
    ]

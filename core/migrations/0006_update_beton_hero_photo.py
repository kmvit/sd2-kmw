from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


def update_beton_hero_photo(apps, schema_editor):
    db = schema_editor.connection.alias
    page = apps.get_model('core', 'Page').objects.using(db).filter(slug='beton').first()
    if page is None:
        return
    photo = Path(settings.BASE_DIR) / 'static/img/sitrak-lineup-beton.jpg'
    with photo.open('rb') as source:
        page.photo.save(photo.name, File(source), save=False)
    page.save(using=db, update_fields=['photo'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_redirect_retired_zhbi_groups'),
    ]

    operations = [
        migrations.RunPython(update_beton_hero_photo, migrations.RunPython.noop),
    ]

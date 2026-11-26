from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


def update_photo(apps, schema_editor):
    sections = apps.get_model('core', 'Section').objects.using(schema_editor.connection.alias)
    section = sections.filter(page__slug='home', key='delivery').first()
    if section is None:
        return

    path = Path(settings.BASE_DIR) / 'static/img/sitrak-lineup-beton.jpg'
    with path.open('rb') as source:
        section.photo.save('sitrak-lineup-home.jpg', File(source), save=False)
    section.save(update_fields=['photo'])


class Migration(migrations.Migration):
    dependencies = [('core', '0017_update_wall_blocks_catalog')]
    operations = [migrations.RunPython(update_photo, migrations.RunPython.noop)]

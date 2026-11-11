from django.conf import settings
from django.db import migrations


def redirect_retired_groups(apps, schema_editor):
    redirects = apps.get_model('redirects', 'Redirect').objects.using(schema_editor.connection.alias)
    for path in (
        '/zhelezobeton/lyuk-smotrovoj-dlya-kolodcev',
        '/zhelezobeton/progony',
        '/produkciya/zhbi/lyuki-kolodcev',
        '/produkciya/zhbi/progony',
    ):
        for old_path in (path, path + '/'):
            redirects.update_or_create(
                site_id=settings.SITE_ID, old_path=old_path,
                defaults={'new_path': '/ZHB-zavod-ZHBI'},
            )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_refresh_zhbi_catalog'),
        ('redirects', '0002_alter_redirect_new_path_help_text'),
    ]

    operations = [
        migrations.RunPython(redirect_retired_groups, migrations.RunPython.noop),
    ]

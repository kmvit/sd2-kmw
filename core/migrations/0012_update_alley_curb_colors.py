from django.db import migrations


def update_alley_colors(apps, schema_editor):
    apps.get_model('catalog', 'ZhbiItem').objects.using(
        schema_editor.connection.alias,
    ).filter(
        group__slug='bordyury', title='Тротуарный (аллейный)',
    ).update(color='Серый, белый, коричневый, красный')


class Migration(migrations.Migration):
    dependencies = [('core', '0011_add_hinged_curb')]
    operations = [
        migrations.RunPython(update_alley_colors, migrations.RunPython.noop),
    ]

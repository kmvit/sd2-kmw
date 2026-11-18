from django.db import migrations


def correct_weights(apps, schema_editor):
    items = apps.get_model('catalog', 'ZhbiItem').objects.using(
        schema_editor.connection.alias,
    ).filter(group__slug='bordyury')
    for title, weight in (
        ('Тротуарный (аллейный)', '36'),
        ('Дорожный', '100'),
        ('Магистральный', '120'),
        ('Блок бетонный Б-5', '200'),
    ):
        items.filter(title=title).update(weight=weight)


class Migration(migrations.Migration):
    dependencies = [('core', '0009_update_owner_message')]

    operations = [
        migrations.RunPython(correct_weights, migrations.RunPython.noop),
    ]

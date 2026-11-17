from django.db import migrations


def update_owner_message(apps, schema_editor):
    Section = apps.get_model('core', 'Section')
    Section.objects.using(schema_editor.connection.alias).filter(
        page__slug='home', key='director',
    ).update(
        lead=(
            'Мы производим товарный бетон, асфальт, железобетонные изделия, тротуарную плитку и бордюры. '
            'У нашей группы четыре площадки по выпуску бетона и собственный карьер. Работаем на современном '
            'оборудовании TEKA, ELKON и CGM. Качество бетона проверяем в своей лаборатории, а доставку '
            'планируем под график заливки на объекте.'
        ),
        note='За качество нашей продукции и выполнение договорённостей с заказчиками я отвечаю лично.',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0008_move_factory_photo_to_home_hero'),
    ]

    operations = [
        migrations.RunPython(update_owner_message, migrations.RunPython.noop),
    ]

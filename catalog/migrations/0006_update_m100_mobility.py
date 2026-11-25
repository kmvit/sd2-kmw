from django.db import migrations


def update_m100_mobility(apps, schema_editor):
    concrete = apps.get_model('catalog', 'ConcreteGrade')
    concrete.objects.using(schema_editor.connection.alias).filter(title='М100').update(
        mobility='П2 (от 5 до 9 см) или П3 (от 10 до 15 см)',
    )


class Migration(migrations.Migration):
    dependencies = [('catalog', '0005_asphaltmix_gost_fields')]
    operations = [migrations.RunPython(update_m100_mobility, migrations.RunPython.noop)]

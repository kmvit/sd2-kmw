from django.db import migrations


def set_laboratory_email(apps, schema_editor):
    settings = apps.get_model('core', 'SiteSettings')
    settings.objects.using(schema_editor.connection.alias).filter(
        pk=1, laboratory_email='',
    ).update(laboratory_email='nlab@sd2kmv.ru')


class Migration(migrations.Migration):
    dependencies = [('core', '0015_laboratory_recipient')]
    operations = [migrations.RunPython(set_laboratory_email, migrations.RunPython.noop)]

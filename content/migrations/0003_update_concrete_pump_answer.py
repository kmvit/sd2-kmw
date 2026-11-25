from django.db import migrations


def update_concrete_pump_answer(apps, schema_editor):
    faq = apps.get_model('content', 'Faq')
    faq.objects.using(schema_editor.connection.alias).filter(
        question='Есть ли у вас бетононасос?',
    ).update(
        answer='10 собственных автобетононасосов со стрелой от 25 до 75 метров. '
               'Насос бронируется вместе с бетоном — одна заявка, один график, один ответственный за заливку.',
    )


class Migration(migrations.Migration):
    dependencies = [('content', '0002_alter_certificate_scan')]

    operations = [migrations.RunPython(update_concrete_pump_answer, migrations.RunPython.noop)]

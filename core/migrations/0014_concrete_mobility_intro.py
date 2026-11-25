from django.db import migrations


def update_intro(apps, schema_editor):
    sections = apps.get_model('core', 'Section').objects.using(schema_editor.connection.alias)
    old = 'Каждая марка отпускается в двух вариантах подвижности: разгрузка по лотку (П2) и под бетононасос (П3).'
    new = 'Для М100–М800 доступны П2 или П3, для М1000 — П5 или самоуплотняющийся бетон SF-2.'
    for section in sections.filter(page__slug='beton', key='grades', lead__contains=old):
        section.lead = section.lead.replace(old, new)
        section.save(update_fields=['lead'])


class Migration(migrations.Migration):
    dependencies = [('core', '0013_update_megapolis_mixes')]
    operations = [migrations.RunPython(update_intro)]

from django.db import migrations


def update_grades(apps, schema_editor):
    grades = apps.get_model('catalog', 'ConcreteGrade').objects.using(schema_editor.connection.alias)
    grades.filter(title__in=['М100', 'М150', 'М200', 'М250', 'М300', 'М350', 'М400',
                             'М450', 'М500', 'М600', 'М800']).update(
        mobility='П2 (от 5 до 9 см) или П3 (от 10 до 15 см)')
    grades.filter(title='М1000').update(mobility='П5 (более 20 см) или самоуплотняющийся SF-2')
    grades.filter(title='М350').update(water='W4–12', frost='F150–200')
    grades.filter(title__in=['М400', 'М450', 'М500', 'М600']).update(water='W6–12', frost='F200–300')
    grades.filter(title__in=['М800', 'М1000']).update(water='W6–20', frost='F500')


class Migration(migrations.Migration):
    dependencies = [('catalog', '0007_alter_concretegrade_mobility')]
    operations = [migrations.RunPython(update_grades)]

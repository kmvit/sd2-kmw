from django.db import migrations
from django.db.models import F, Value
from django.db.models.functions import Replace


def add_hinged_curb(apps, schema_editor):
    db = schema_editor.connection.alias
    Group = apps.get_model('catalog', 'ZhbiGroup')
    Item = apps.get_model('catalog', 'ZhbiItem')
    group = Group.objects.using(db).filter(slug='bordyury').first()
    if group is None:
        return
    items = Item.objects.using(db).filter(group=group)
    road = items.filter(title='Дорожный').first()
    order = road.order if road else 50
    if not items.filter(title='Тротуарный (шарнирный)').exists():
        items.filter(order__gte=order).update(order=F('order') + 10)
    Item.objects.using(db).update_or_create(
        group=group, title='Тротуарный (шарнирный)',
        defaults={
            'frost': 'F150', 'weight': '12', 'length': '330', 'width': '80',
            'height': '200', 'color': 'Серый, белый, коричневый, красный',
            'price': None, 'price_label': 'Договорная', 'price_prefix': '',
            'band': 'Бордюр садовый (тротуарный)', 'order': order, 'published': True,
        },
    )
    Group.objects.using(db).filter(pk=group.pk).update(
        kinds_label='5 видов',
        summary=Replace('summary', Value('4 вида'), Value('5 видов')),
        seo_description=Replace('seo_description', Value('4 вида'), Value('5 видов')),
    )


class Migration(migrations.Migration):
    dependencies = [('core', '0010_correct_curb_weights')]
    operations = [migrations.RunPython(add_hinged_curb, migrations.RunPython.noop)]

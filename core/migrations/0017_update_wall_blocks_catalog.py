from django.db import migrations


BLOCKS = [
    ('Блок стеновой 2-х секционный (бетонный) облегченный Зенит', 'М35', 'F 25', '0,75 Вт/(м·°С)', '390 × 190 × 190', '18,5 кг'),
    ('Блок стеновой 4-х секционный (бетонный) облегченный Зенит', 'М35', 'F 25', '0,75 Вт/(м·°С)', '390 × 190 × 190', '19,55 кг'),
    ('Блок стеновой усиленный (бетонный) Зенит', 'М35', 'F 25', '0,75 Вт/(м·°С)', '390 × 190 × 190', '24,0 кг'),
    ('Полублок стеновой (бетонный) Зенит', 'М35', 'F 25', '0,75 Вт/(м·°С)', '390 × 120 × 190', '12,8 кг'),
]


def update_wall_blocks(apps, schema_editor):
    db = schema_editor.connection.alias
    blocks = apps.get_model('catalog', 'WallBlock').objects.using(db)
    blocks.exclude(title__in=[row[0] for row in BLOCKS]).filter(published=True).update(published=False)
    for position, (title, grade, frost, conductivity, size, weight) in enumerate(BLOCKS, 1):
        blocks.update_or_create(title=title, defaults={
            'grade': grade, 'frost': frost, 'conductivity': conductivity, 'size': size,
            'weight': weight, 'price': None, 'price_prefix': '', 'price_label': 'Договорная',
            'published': True, 'order': position * 10,
        })

    groups = apps.get_model('catalog', 'ZhbiGroup').objects.using(db)
    groups.filter(slug='stenovye-bloki').update(
        kinds_label='4 вида',
        seo_description='Четыре вида стеновых бетонных блоков Зенит по ГОСТ 6133-2019. До 3 миллионов блоков в год, отгрузка со склада завода в Пятигорске.',
        description='<p>Четыре вида блоков объёмного вибропрессования на оборудовании ЗЕНИТ по ГОСТ 6133-2019. До 3 миллионов блоков в год — отгрузка со склада в Пятигорске.</p><p>Из блоков строят частные дома, гаражи, хозпостройки, заборы и межкомнатные перегородки.</p><p>На каждую партию — паспорт качества.</p>',
    )
    sections = apps.get_model('core', 'Section').objects.using(db)
    sections.filter(page__slug='zhbi', key='blocks').update(
        lead='Четыре вида блоков объёмного вибропрессования на оборудовании ЗЕНИТ по ГОСТ 6133-2019. До 3 миллионов блоков в год — отгрузка со склада в Пятигорске.',
        note='Паспорт качества установленного ГОСТом образца выдаём на каждую партию.',
    )


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0016_set_laboratory_email'),
        ('catalog', '0008_concrete_specifications'),
    ]
    operations = [migrations.RunPython(update_wall_blocks, migrations.RunPython.noop)]

# -*- coding: utf-8 -*-
"""Продукция завода: марки бетона, растворы, инертные, изделия ЖБИ.

Каждая таблица вёрстки — своя модель: колонки у них разные, а в админке
удобнее править настоящие поля, чем универсальный набор «колонка 1, колонка 2».

Цена везде необязательна: пустая означает «по запросу». Так завод открывает
прайс по частям — сейчас открыт только карьер и бетононасос-миксер.
"""
from django.db import models
from django.urls import reverse

from core.models import Ordered


class Priced(models.Model):
    """Цена, которой может не быть.

    На сайте цены закрыты почти везде, и это решение завода, а не недоработка:
    стоимость зависит от объёма, плеча доставки и способа подачи. Поэтому цена
    хранится отдельным числом, а вместо пустой показывается подпись.
    """

    price = models.PositiveIntegerField('Цена, ₽', null=True, blank=True,
                                        help_text='Пусто — вместо цены покажем подпись ниже')
    price_prefix = models.CharField('Приписка перед ценой', max_length=10, blank=True, default='от',
                                    help_text='Например «от». Пусто — покажем точную цену')
    price_label = models.CharField('Чем заменить пустую цену', max_length=40, blank=True,
                                   default='По запросу',
                                   help_text='«По запросу» или «Договорная»')

    class Meta:
        abstract = True


class Direction(Ordered):
    """Направление производства — четыре строки-реестра на главной."""

    title = models.CharField('Название', max_length=120)
    text = models.TextField('Описание', blank=True)
    photo = models.ImageField('Фото', upload_to='directions/', blank=True)
    chips = models.CharField('Бейджи', max_length=250, blank=True,
                             help_text='Через точку с запятой. Бейдж с «!» в конце — выделенный: '
                                       'Кубовидный щебень!; Мытый песок')
    price_value = models.CharField('Цена в строке', max_length=60, blank=True,
                                   default='по запросу')
    price_note = models.CharField('Подпись под ценой', max_length=120, blank=True,
                                  help_text='Например «за м³ с доставкой»')
    url_name = models.CharField('Маршрут страницы', max_length=60, blank=True)
    anchor = models.CharField('Якорь', max_length=40, blank=True, default='request')
    link_label = models.CharField('Подпись ссылки', max_length=60, blank=True,
                                  default='Узнать цену →')

    class Meta(Ordered.Meta):
        verbose_name = 'Направление на главной'
        verbose_name_plural = 'Направления на главной'

    def __str__(self):
        return self.title

    @property
    def chip_list(self):
        """Бейджи строкой → список пар (текст, выделенный)."""
        out = []
        for chunk in self.chips.split(';'):
            chunk = chunk.strip()
            if chunk:
                out.append((chunk.rstrip('!').strip(), chunk.endswith('!')))
        return out


class ConcreteGrade(Ordered, Priced):
    """Марка товарного бетона: строка таблицы на странице бетона."""

    group = models.CharField('Раздел таблицы', max_length=120, blank=True,
                             help_text='Строки с одинаковым разделом идут вместе, '
                                       'а название показывается полосой. Пусто — без полосы')
    title = models.CharField('Марка', max_length=40, help_text='Например М300')
    grade_class = models.CharField('Класс', max_length=40, blank=True, help_text='Например В22,5')
    water = models.CharField('Водонепроницаемость', max_length=30, blank=True, help_text='W4')
    frost = models.CharField('Морозостойкость', max_length=30, blank=True, help_text='F150')
    mobility = models.CharField('Подвижность', max_length=120, blank=True,
                                help_text='П2 (15 см) или П3 под насос')

    class Meta(Ordered.Meta):
        verbose_name = 'Марка бетона'
        verbose_name_plural = 'Бетон: марки'

    def __str__(self):
        return self.title


class Mortar(Ordered, Priced):
    """Строительный раствор: кладочный, штукатурный, с жизнеспособностью 24/48 ч."""

    group = models.CharField('Раздел таблицы', max_length=120, blank=True)
    title = models.CharField('Наименование', max_length=150)
    grade = models.CharField('Марка', max_length=40, blank=True, help_text='М50, М75, М100')
    mobility = models.CharField('Подвижность', max_length=40, blank=True, help_text='Пк3')
    purpose = models.CharField('Назначение', max_length=250, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Раствор'
        verbose_name_plural = 'Бетон: растворы'

    def __str__(self):
        return f'{self.title} {self.grade}'.strip()


class Aggregate(Ordered, Priced):
    """Позиция прайса карьера: щебень, песок, щебёночно-песчаная смесь, минпорошок."""

    group = models.CharField('Раздел таблицы', max_length=150, blank=True,
                             help_text='Например «Щебень мытый · М1000 · морозостойкость F200»')
    title = models.CharField('Наименование', max_length=150)
    fraction = models.CharField('Фракция', max_length=60, blank=True, help_text='5–20 мм')
    gost = models.CharField('ГОСТ', max_length=60, blank=True, help_text='8267-93')
    spec = models.CharField('Характеристики', max_length=200, blank=True,
                            help_text='Кубовидный, 1-я категория / модуль крупности 2,5–3,0')

    class Meta(Ordered.Meta):
        verbose_name = 'Щебень и песок'
        verbose_name_plural = 'Карьер: щебень и песок'

    def __str__(self):
        return f'{self.title} {self.fraction}'.strip()


class AsphaltMix(Ordered, Priced):
    """Асфальтобетонная смесь по ГОСТ 9128-2009."""

    title = models.CharField('Вид смеси', max_length=120)
    mix_type = models.CharField('Тип', max_length=40, blank=True, help_text='тип Б')
    grade = models.CharField('Марка', max_length=40, blank=True, help_text='марка II')
    purpose = models.CharField('Область применения', max_length=300, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Асфальтобетонная смесь'
        verbose_name_plural = 'Асфальт: смеси'

    def __str__(self):
        return self.title


class WallBlock(Ordered, Priced):
    """Стеновой блок объёмного вибропрессования."""

    title = models.CharField('Вид блока', max_length=150)
    grade = models.CharField('Марка', max_length=40, blank=True, help_text='М50')
    frost = models.CharField('Морозостойкость', max_length=30, blank=True, help_text='F35')
    conductivity = models.CharField('Теплопроводность', max_length=40, blank=True,
                                    help_text='0,24 Вт/(м·°С)')
    size = models.CharField('Размер, мм', max_length=60, blank=True, help_text='390 × 190 × 190')
    weight = models.CharField('Вес', max_length=30, blank=True, help_text='19 кг')

    class Meta(Ordered.Meta):
        verbose_name = 'Стеновой блок'
        verbose_name_plural = 'ЖБИ: стеновые блоки'

    def __str__(self):
        return self.title


class PavingModel(Ordered, Priced):
    """Модель тротуарной плитки: размеры и расход на поддон."""

    title = models.CharField('Модель', max_length=120)
    size = models.CharField('Размер, мм', max_length=120, blank=True)
    thickness = models.CharField('Толщина', max_length=40, blank=True, help_text='60 мм')
    per_pack = models.CharField('В упаковке', max_length=40, blank=True, help_text='9,6 м²')
    pallet_weight = models.CharField('Вес поддона', max_length=40, blank=True, help_text='1,3 т')

    class Meta(Ordered.Meta):
        verbose_name = 'Модель плитки'
        verbose_name_plural = 'Плитка: модели'

    def __str__(self):
        return self.title


class PavingColor(Ordered):
    """Цвет плитки: базовый или смешение серии «Мегаполис»."""

    title = models.CharField('Название', max_length=60)
    is_mix = models.BooleanField('Серия «Мегаполис»', default=False,
                                 help_text='Смешение двух-трёх цветов в фактурном слое')
    sample = models.ImageField('Фото образца', upload_to='paving/', blank=True,
                               help_text='Снимок выкладки — пока не загружен, показываем только название')

    class Meta(Ordered.Meta):
        verbose_name = 'Цвет плитки'
        verbose_name_plural = 'Плитка: цвета'

    def __str__(self):
        return self.title


class ZhbiGroup(Ordered):
    """Группа изделий ЖБИ — плитка каталога и своя страница товара.

    `legacy_url` хранит адрес карточки на старом сайте: по нему команда
    заводит 301-редирект, иначе при переезде потеряется поисковый трафик,
    который эти страницы собирали годами.
    """

    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('Адрес страницы', max_length=200, unique=True)
    kinds_label = models.CharField('Сколько видов', max_length=40, blank=True,
                                   help_text='Подпись на плитке каталога, например «9 видов»')
    photo = models.ImageField('Фото изделия', upload_to='zhbi/', blank=True)
    summary = models.CharField('Кратко', max_length=300, blank=True,
                               help_text='Строка под заголовком на странице товара')
    description = models.TextField('Описание', blank=True,
                                   help_text='Назначение изделия. Можно с HTML')
    gost = models.CharField('ГОСТ или ТУ', max_length=120, blank=True)
    note = models.TextField('Примечание под таблицей', blank=True)
    legacy_url = models.CharField('Адрес на старом сайте', max_length=200, blank=True,
                                  help_text='Например /zhelezobeton/progony — для 301-редиректа')
    custom_template = models.CharField(
        'Свой шаблон', max_length=60, blank=True,
        help_text='Для групп с особой вёрсткой — например плитка с моделями и цветами. '
                  'Пусто — обычная таблица характеристик')
    seo_title = models.CharField('SEO-заголовок (title)', max_length=250, blank=True)
    seo_description = models.TextField('SEO-описание (description)', blank=True, max_length=400)

    class Meta(Ordered.Meta):
        verbose_name = 'Группа изделий ЖБИ'
        verbose_name_plural = 'ЖБИ: группы изделий'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('zhbi_item', args=[self.slug])


class ZhbiItem(Ordered, Priced):
    """Позиция внутри группы ЖБИ — строка таблицы характеристик.

    Набор колонок у групп разный: у колец важен диаметр, у перемычек — несущая
    способность, у плит — объём бетона. Поэтому поля общие и почти все
    необязательные, а таблица показывает только те, что заполнены в группе.
    """

    group = models.ForeignKey(ZhbiGroup, verbose_name='Группа', on_delete=models.CASCADE,
                              related_name='items')
    band = models.CharField('Раздел таблицы', max_length=150, blank=True,
                            help_text='Полоса-разделитель, например «Диаметром 1,2 метра»')
    title = models.CharField('Наименование', max_length=150, help_text='Марка изделия, например ПН-10')
    concrete_class = models.CharField('Класс бетона', max_length=40, blank=True)
    frost = models.CharField('Морозостойкость', max_length=30, blank=True)
    volume = models.CharField('Объём бетона, м³', max_length=30, blank=True)
    weight = models.CharField('Вес, кг', max_length=30, blank=True)
    length = models.CharField('Длина, мм', max_length=30, blank=True)
    width = models.CharField('Ширина, мм', max_length=30, blank=True)
    height = models.CharField('Высота, мм', max_length=30, blank=True)
    diameter = models.CharField('Диаметр, мм', max_length=30, blank=True)
    color = models.CharField('Цвет', max_length=60, blank=True)
    capacity = models.CharField('Несущая способность', max_length=60, blank=True)
    note = models.CharField('Примечание', max_length=200, blank=True)

    class Meta(Ordered.Meta):
        verbose_name = 'Позиция ЖБИ'
        verbose_name_plural = 'ЖБИ: позиции'

    def __str__(self):
        return f'{self.group.title} · {self.title}'


class DeliveryZone(Ordered, Priced):
    """Направление доставки бетона: населённые пункты и стоимость рейса."""

    title = models.CharField('Направление', max_length=150)
    settlements = models.CharField('Населённые пункты', max_length=400, blank=True,
                                   help_text='Через запятую — как в прайсе')

    class Meta(Ordered.Meta):
        verbose_name = 'Направление доставки'
        verbose_name_plural = 'Доставка: направления'

    def __str__(self):
        return self.title


class ConcretePump(Ordered, Priced):
    """Автобетононасос: длина подачи, площадка под опоры, порядок расчёта."""

    title = models.CharField('Техника', max_length=150)
    reach = models.CharField('Длина подачи', max_length=60, blank=True, help_text='32 метра')
    pad = models.CharField('Площадка под насос', max_length=60, blank=True, help_text='9 × 8 метров')
    billing = models.CharField('Как считается', max_length=200, blank=True)
    price_text = models.CharField('Стоимость', max_length=120, blank=True,
                                  help_text='Если тариф сложный: «3 200 ₽ + 400 ₽/м³». '
                                            'Заполнено — показывается вместо числовой цены')

    class Meta(Ordered.Meta):
        verbose_name = 'Бетононасос'
        verbose_name_plural = 'Доставка: бетононасосы'

    def __str__(self):
        return self.title

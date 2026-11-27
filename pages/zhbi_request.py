from decimal import Decimal

from django import forms

from catalog.models import PavingModel, WallBlock
from leads.forms import LeadForm


class ZhbiRequestForm(LeadForm):
    variant = forms.ChoiceField(required=False, label='Изделие / типоразмер')
    quantity = forms.DecimalField(min_value=Decimal('0.01'), max_digits=10, decimal_places=2)
    category = 'ЖБИ, плитка, бордюр'

    def __init__(self, group, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.fields['variant'].choices = [('', 'Уточнить при расчёте'), *self.variant_choices()]
        self.fields['variant'].widget.attrs.update({'class': 'f-input', 'id': 'r-variant'})
        if group.order_unit == 'шт.':
            self.fields['quantity'] = forms.IntegerField(min_value=1, max_value=9999999999)
        self.fields['quantity'].label = f'Количество, {group.order_unit}'
        self.fields['quantity'].widget.attrs.update({'class': 'f-input', 'id': 'r-quantity'})

    def variant_choices(self):
        if self.group.custom_template == 'zhbi_plitka':
            return [(str(item.pk), ' · '.join(filter(None, (item.title, item.size, item.thickness))))
                    for item in PavingModel.objects.filter(published=True)]
        if self.group.custom_template == 'zhbi_bloki':
            items = WallBlock.objects.filter(published=True)
        else:
            items = self.group.items.filter(published=True)
        return [(str(item.pk), item.title) for item in items]

    def save(self, commit=True):
        lead = super().save(commit=False)
        selected = self.cleaned_data['variant']
        quantity = format(Decimal(self.cleaned_data['quantity']).normalize(), 'f').replace('.', ',')
        details = [f'Изделие: {self.group.title}', f'Количество: {quantity} {self.group.order_unit}']
        if selected:
            details.append(f'Типоразмер: {dict(self.fields["variant"].choices)[selected]}')
        if lead.details:
            details.append(lead.details)
        lead.product = self.category
        lead.details = '\n'.join(details)
        lead.page = self.group.get_absolute_url()
        if commit:
            lead.save()
        return lead

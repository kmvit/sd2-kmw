# -*- coding: utf-8 -*-
"""Формы сайта: заявка на расчёт и письмо директору."""
from django import forms

from .models import DirectorMessage, Lead


class HoneypotMixin(forms.Form):
    """Скрытое поле-ловушка.

    Человек его не видит и не заполняет, а простые спам-боты заполняют все поля
    подряд. Так отсекается основной поток мусора без капчи, которую пришлось бы
    показывать живым посетителям.
    """

    website = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Заявка не отправлена')
        return ''


class LeadForm(HoneypotMixin, forms.ModelForm):
    agree = forms.BooleanField(
        required=True, error_messages={'required': 'Отметьте согласие на обработку данных'})

    class Meta:
        model = Lead
        fields = ['name', 'phone', 'product', 'details']
        error_messages = {
            'name': {'required': 'Как к вам обращаться?'},
            'phone': {'required': 'Оставьте телефон — без него не перезвонить'},
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if sum(c.isdigit() for c in phone) < 10:
            raise forms.ValidationError('Проверьте номер телефона')
        return phone


class DirectorMessageForm(HoneypotMixin, forms.ModelForm):
    class Meta:
        model = DirectorMessage
        fields = ['message', 'contact']
        error_messages = {'message': {'required': 'Напишите, что случилось'}}

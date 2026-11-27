from django import forms
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from leads.forms import HoneypotMixin
from leads.models import Lead
from leads.notify import notify_laboratory


class LaboratoryForm(HoneypotMixin):
    phone = forms.CharField(label='Телефон', max_length=40,
                            widget=forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel', 'class': 'f-input'}))
    details = forms.CharField(label='Что требуется проверить', max_length=3000,
                              widget=forms.Textarea(attrs={'class': 'f-input', 'rows': 3}))
    agree = forms.BooleanField()

    def clean_phone(self):
        value = self.cleaned_data['phone']
        if sum(ch.isdigit() for ch in value) < 10:
            raise forms.ValidationError('Проверьте номер телефона.')
        return value


@require_http_methods(['GET', 'POST'])
def request_service(request, protocol):
    service = 'Запрос протокола' if protocol else 'Испытание'
    form = LaboratoryForm(request.POST if request.method == 'POST' else None)
    if protocol:
        form.fields['details'].label = 'Номер накладной или дата поставки (если известны)'
        form.fields['details'].required = False
    if request.method == 'POST' and form.is_valid():
        lead = Lead.objects.create(name=service, product=service, phone=form.cleaned_data['phone'],
                                   details=form.cleaned_data['details'], page=request.path)
        notify_laboratory(lead)
        return redirect(request.path + '?accepted=1')
    return render(request, 'pages/laboratory_request.html', {
        'service': service, 'protocol': protocol, 'form': form,
        'accepted': request.method == 'GET' and request.GET.get('accepted') == '1',
    })

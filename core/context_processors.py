# -*- coding: utf-8 -*-
"""Общие данные сайта доступны в каждом шаблоне как `site`."""
from .models import SiteSettings


def site(request):
    return {'site': SiteSettings.get()}

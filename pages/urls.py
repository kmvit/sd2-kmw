# -*- coding: utf-8 -*-
"""Маршруты сайта. Адреса взяты из согласованного аудита — под них же
заводится карта 301-редиректов со старого сайта."""
from django.urls import path

from . import views

urlpatterns = [
    path(url, views.make_page_view(template, active, name), name=name)
    for url, name, template, active in views.PAGES
]

urlpatterns += [
    path('produkciya/zhbi/<slug:slug>/', views.zhbi_item, name='zhbi_item'),
    path('zayavka/', views.lead_create, name='lead_create'),
    path('pismo-direktoru/', views.director_create, name='director_create'),
    path('robots.txt', views.robots_txt, name='robots'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap'),
]

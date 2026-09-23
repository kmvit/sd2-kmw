#!/usr/bin/env python3
"""Сборка статических страниц макета из общих частей.

Шапка, футер, форма заявки, мобильное меню живут в src/partials/ в одном
экземпляре — иначе правка логотипа означала бы обход девяти файлов.
Контент страницы лежит в src/pages/<имя>.html и начинается с блока метаданных
в HTML-комментарии:

    <!--meta
    title: Заголовок вкладки
    description: Описание для поисковой выдачи
    nav: beton          # какой пункт меню подсветить (необязательно)
    product: beton      # что выбрать в селекте заявки (необязательно)
    -->

Запуск:  python3 build.py            # для тестового домена: сайт закрыт от индексации
         python3 build.py --prod     # для боевого домена: индексация разрешена
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
PARTIALS = SRC / "partials"

# пункт меню -> плейсхолдер активного состояния в шапке
NAV_KEYS = {
    "products": "{{ACT_PRODUCTS}}",
    "dostavka": "{{ACT_DOSTAVKA}}",
    "lab": "{{ACT_LAB}}",
    "karer": "{{ACT_KARER}}",
    "obekty": "{{ACT_OBEKTY}}",
    "kontakty": "{{ACT_KONTAKTY}}",
}

# порядок опций в селекте заявки: выбранный товар поднимается наверх
FORM_OPTIONS = [
    ("beton", "Бетон или раствор"),
    ("zhbi", "ЖБИ, плитка, бордюр"),
    ("asfalt", "Асфальтобетон"),
    ("karer", "Щебень или песок"),
]


# Пока сайт живёт на техническом домене, он должен быть закрыт от поисковиков:
# мета-тег в каждой странице плюс robots.txt. Сборка с --prod снимает запрет —
# делать это нужно одним действием и осознанно, в день переезда на sd2-kmv.ru.
NOINDEX_META = '<meta name="robots" content="noindex, nofollow" />\n'

ROBOTS_CLOSED = """# Тестовая площадка — сайт закрыт от индексации.
# Боевой robots.txt собирается командой: python3 build.py --prod
User-agent: *
Disallow: /
"""

ROBOTS_OPEN = """User-agent: *
Allow: /

Sitemap: https://sd2-kmv.ru/sitemap.xml
"""


def parse_meta(text):
    """Отделяет блок метаданных от контента страницы."""
    m = re.match(r"\s*<!--meta\s*(.*?)-->\s*", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).strip().splitlines():
        line = line.split("#")[0].strip()
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, text[m.end():]


def build_form_options(preselect):
    """Товар страницы идёт первым — он же выбран по умолчанию."""
    ordered = sorted(FORM_OPTIONS, key=lambda o: o[0] != preselect)
    return "".join(f"<option>{label}</option>" for _, label in ordered)


def build_page(path, head, foot, scripts, prod=False):
    meta, content = parse_meta(path.read_text(encoding="utf-8"))
    if "title" not in meta:
        sys.exit(f"{path.name}: в блоке meta нет title")

    html = head.replace("{{TITLE}}", meta["title"])
    html = html.replace("{{DESCRIPTION}}", meta.get("description", ""))
    html = html.replace("{{ROBOTS}}", "" if prod else NOINDEX_META)

    active = meta.get("nav", "")
    for key, placeholder in NAV_KEYS.items():
        html = html.replace(placeholder, " act" if key == active else "")

    tail = foot.replace("{{FORM_OPTIONS}}", build_form_options(meta.get("product", "")))
    tail = tail.replace("{{SCRIPTS}}", scripts)

    out = ROOT / path.name
    out.write_text(html + "\n" + content.strip() + "\n\n" + tail, encoding="utf-8")
    return out.name


def main():
    prod = "--prod" in sys.argv
    head = (PARTIALS / "head.html").read_text(encoding="utf-8")
    foot = (PARTIALS / "foot.html").read_text(encoding="utf-8")
    scripts_file = PARTIALS / "scripts.html"
    scripts = scripts_file.read_text(encoding="utf-8") if scripts_file.exists() else ""

    pages = sorted(PAGES.glob("*.html"))
    if not pages:
        sys.exit("В src/pages/ нет страниц")
    for page in pages:
        print("собрано:", build_page(page, head, foot, scripts, prod))

    (ROOT / "robots.txt").write_text(ROBOTS_OPEN if prod else ROBOTS_CLOSED,
                                     encoding="utf-8")
    print("собрано: robots.txt —",
          "индексация разрешена" if prod else "сайт закрыт от индексации")


if __name__ == "__main__":
    main()

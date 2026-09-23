#!/usr/bin/env python3
"""Съёмка страниц макета в JPG — для передачи заказчику.

Кладёт полностраничные снимки в docs/mockups/desktop/ и docs/mockups/mobile/.
Страницы берутся из корня проекта; сервер поднимается на время съёмки сам.

Запуск:  python3 shots.py            # все страницы
         python3 shots.py index      # только index.html
"""

import http.server
import socketserver
import sys
import threading
from functools import partial
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
OUT = ROOT / "docs" / "mockups"
PORT = 8912

# порядок как в меню — чтобы снимки листались в логике сайта
ORDER = [
    "index", "beton", "zhbi", "zhbi-plitka", "asfalt", "karer",
    "dostavka", "laboratoriya", "obekty", "kontakty", "politika",
]

VIEWS = [("desktop", 1600, 1000, 1), ("mobile", 390, 844, 2)]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Лог запросов не нужен — он забивает вывод съёмки."""

    def log_message(self, *args):
        pass


def serve():
    handler = partial(QuietHandler, directory=str(ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def shoot(page, name, folder, index):
    page.goto(f"http://127.0.0.1:{PORT}/{name}.html", wait_until="networkidle")
    # плавающие кнопки и мобильное меню — интерактив, на статичном макете лишний
    page.add_style_tag(content=".floats{display:none!important}.mmenu{display:none!important}")
    # снимок делается сразу всей страницей, поэтому отложенные картинки
    # (сертификаты, логотипы, карта) не успевают загрузиться — снимаем lazy
    # и прокручиваем страницу, чтобы браузер дошёл до каждой из них
    page.evaluate("""() => {
      document.querySelectorAll('img[loading="lazy"], iframe[loading="lazy"]')
        .forEach(el => el.loading = 'eager');
      return new Promise(done => {
        let y = 0;
        const step = () => {
          y += window.innerHeight;
          window.scrollTo(0, y);
          if (y < document.body.scrollHeight) setTimeout(step, 90);
          else { window.scrollTo(0, 0); done(); }
        };
        step();
      });
    }""")
    page.wait_for_load_state("networkidle")
    page.wait_for_function(
        "() => Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
        timeout=15000,
    )
    # виджет карты грузит тайлы своим скриптом — networkidle его не ловит.
    # На очень длинных страницах (главная) карта в цельный снимок всё равно не
    # попадает и остаётся серым блоком — для макета это признано допустимым.
    page.wait_for_timeout(3000 if page.query_selector("iframe") else 600)
    path = OUT / folder / f"{index:02d}-{name}.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)

    page.screenshot(path=str(path), full_page=True, type="jpeg", quality=88)
    return path


def main():
    wanted = sys.argv[1:] or ORDER
    names = [n for n in ORDER if n in wanted]
    missing = [n for n in wanted if not (ROOT / f"{n}.html").exists()]
    if missing:
        sys.exit("нет таких страниц: " + ", ".join(missing))

    httpd = serve()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for folder, width, height, dsf in VIEWS:
                ctx = browser.new_context(
                    viewport={"width": width, "height": height},
                    device_scale_factor=dsf,
                    is_mobile=(folder == "mobile"),
                )
                page = ctx.new_page()
                for i, name in enumerate(names, 1):
                    path = shoot(page, name, folder, ORDER.index(name) + 1)
                    kb = path.stat().st_size // 1024
                    print(f"{folder}: {path.name} ({kb} КБ)")
                ctx.close()
            browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    main()

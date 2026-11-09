"""Replace the obsolete certificate gallery with the supplied current PDFs."""
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from content.models import Certificate
from core.models import Section
from pages.seed import directories, home


class Command(BaseCommand):
    help = 'Заменить старые сертификаты пятью PDF из static/docs/certs'

    def handle(self, *args, **options):
        static = Path(settings.BASE_DIR) / 'static'
        rows = directories.CERTIFICATES
        for _, _, scan, thumb, _ in rows:
            for rel in (scan, thumb):
                if not (static / rel).is_file():
                    raise CommandError(f'Не найден файл сертификата: {rel}')

        current = list(Certificate.objects.order_by('order', 'pk'))
        up_to_date = len(current) == len(rows) and all(
            cert.title == title
            and cert.gost == standard
            and cert.valid_until == date.fromisoformat(until)
            and Path(cert.scan.name).name.startswith(Path(scan).stem)
            and Path(cert.thumb.name).name.startswith(Path(thumb).stem)
            for cert, (title, standard, scan, thumb, until) in zip(current, rows)
        )

        lead = next(row[3] for row in home.SECTIONS if row[0] == 'certs')
        section = Section.objects.filter(page__slug='home', key='certs').first()
        if section and section.lead != lead:
            section.lead = lead
            section.save(update_fields=['lead'])

        if up_to_date:
            self.stdout.write('сертификаты уже обновлены')
            return

        obsolete = [(cert.scan.storage, cert.scan.name) for cert in current if cert.scan.name]
        obsolete += [(cert.thumb.storage, cert.thumb.name) for cert in current if cert.thumb.name]
        created = []
        try:
            with transaction.atomic():
                Certificate.objects.all().delete()
                for order, (title, standard, scan, thumb, until) in enumerate(rows, 1):
                    cert = Certificate(title=title, gost=standard,
                                       valid_until=date.fromisoformat(until), order=order * 10)
                    with (static / scan).open('rb') as source:
                        cert.scan.save(Path(scan).name, File(source), save=False)
                    created.append((cert.scan.storage, cert.scan.name))
                    with (static / thumb).open('rb') as source:
                        cert.thumb.save(Path(thumb).name, File(source), save=False)
                    created.append((cert.thumb.storage, cert.thumb.name))
                    cert.save()
        except Exception:
            for storage, name in created:
                storage.delete(name)
            raise

        live_names = {name for _, name in created}
        for storage, name in obsolete:
            if name not in live_names:
                storage.delete(name)
        self.stdout.write(self.style.SUCCESS(f'заменено сертификатов: {len(rows)}'))

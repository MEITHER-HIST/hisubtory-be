import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from subway.models import Line

class Command(BaseCommand):
    help = "Seed subway lines from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="subway/management/seed_data/lines.csv",
            help="Path to lines csv",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"]).resolve()
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"CSV not found: {file_path}"))
            return

        created, updated = 0, 0
        with file_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get("line_name") or "").strip()
                if not name:
                    continue
                color = (row.get("line_color") or "").strip() or None

                obj, was_created = Line.objects.update_or_create(
                    line_name=name,
                    defaults={"line_color": color},
                )
                created += int(was_created)
                updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(f"Done. created={created}, updated={updated}"))
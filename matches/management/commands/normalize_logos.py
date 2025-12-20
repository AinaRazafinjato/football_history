from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil

from matches.models import League, Team


class Command(BaseCommand):
    help = 'Normalize logo file paths in League and Team.logo.name (dry-run by default).'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Apply changes (move files and save models).')

    def handle(self, *args, **options):
        apply_changes = options['apply']

        # Determine static dir
        static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
        if static_dirs:
            static_root = static_dirs[0]
        else:
            static_root = os.path.join(settings.BASE_DIR, 'static')

        media_root = getattr(settings, 'MEDIA_ROOT', None)

        total = 0
        changed = 0
        skipped = 0

        def normalize_obj(obj):
            nonlocal total, changed, skipped
            total += 1
            name = obj.logo.name if obj.logo else None
            if not name:
                skipped += 1
                return

            # Desired prefix
            desired = name
            if not name.startswith('logos/'):
                desired = 'logos/' + name.lstrip('/')

            if name == desired:
                # already good
                skipped += 1
                return

            # Check media
            media_path = os.path.join(media_root, desired) if media_root else None
            static_desired_path = os.path.join(static_root, desired)
            static_old_path = os.path.join(static_root, name)

            if media_root and os.path.exists(media_path):
                self.stdout.write(f"Would set {obj} logo.name -> {desired} (exists in MEDIA)")
                if apply_changes:
                    obj.logo.name = desired
                    obj.save(update_fields=['logo'])
                    changed += 1
                return

            if os.path.exists(static_desired_path):
                self.stdout.write(f"Would set {obj} logo.name -> {desired} (exists in STATIC)")
                if apply_changes:
                    obj.logo.name = desired
                    obj.save(update_fields=['logo'])
                    changed += 1
                return

            # If file exists at static_old_path but not under desired, move it
            if os.path.exists(static_old_path):
                self.stdout.write(f"Found file at static/{name}; will move to static/{desired}")
                if apply_changes:
                    dest_dir = os.path.dirname(static_desired_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(static_old_path, static_desired_path)
                    obj.logo.name = desired
                    obj.save(update_fields=['logo'])
                    changed += 1
                return

            # Nothing found
            self.stdout.write(f"Skipping {obj}: file not found for '{name}' or '{desired}'")
            skipped += 1

        # Process leagues
        self.stdout.write('Scanning League.logo...')
        for league in League.objects.filter(logo__isnull=False):
            normalize_obj(league)

        # Process teams
        self.stdout.write('Scanning Team.logo...')
        for team in Team.objects.filter(logo__isnull=False):
            normalize_obj(team)

        self.stdout.write('\nSummary:')
        self.stdout.write(f'  Total processed: {total}')
        self.stdout.write(f'  Changed: {changed}')
        self.stdout.write(f'  Skipped (already ok or missing): {skipped}')

        if not apply_changes:
            self.stdout.write('\nDry-run complete. Re-run with --apply to perform changes.')

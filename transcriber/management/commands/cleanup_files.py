import os
from django.core.management.base import BaseCommand
from django.conf import settings
from transcriber.models import AudioTranscription

class Command(BaseCommand):
    help = 'Cleans up orphan audio files that are on disk but not in the database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting orphan file cleanup...'))
        try:
            db_files = set(AudioTranscription.objects.values_list('audio_file', flat=True))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Could not retrieve files from database: {e}"))
            return

        wavs_dir = os.path.join(settings.MEDIA_ROOT, 'wavs')
        if not os.path.isdir(wavs_dir):
            self.stdout.write(self.style.SUCCESS('WAVs directory does not exist. No cleanup needed.'))
            return
            
        disk_files = set()
        for filename in os.listdir(wavs_dir):
            if filename.lower().endswith('.wav'):
                disk_files.add(os.path.join('wavs', filename).replace('\\', '/'))

        orphan_files = disk_files - db_files

        if not orphan_files:
            self.stdout.write(self.style.SUCCESS('No orphan files found. Everything is clean!'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(orphan_files)} orphan files to delete.'))

        deleted_count = 0
        for orphan_file_rel_path in orphan_files:
            full_path = os.path.join(settings.MEDIA_ROOT, orphan_file_rel_path)
            try:
                os.remove(full_path)
                self.stdout.write(f'  - Deleted: {full_path}')
                deleted_count += 1
            except OSError as e:
                self.stderr.write(self.style.ERROR(f'  - Error deleting {full_path}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'Cleanup complete. Successfully deleted {deleted_count} orphan file(s).'))
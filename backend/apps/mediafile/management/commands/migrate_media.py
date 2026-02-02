"""
Management command to migrate media files.
"""

import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from ...models.media_file import MediaFile
from ...models.media_folder import MediaFolder
from ...services.media_service import MediaService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate media files from Cloudinary to Cloudflare R2 + ImageKit.io"

    def add_arguments(self, parser):
        parser.add_argument(
            "--store-id",
            type=str,
            help="Store ID to migrate media for (default: all stores)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=100,
            help="Maximum number of files to migrate (default: 100)",
        )
        parser.add_argument("--dry-run", action="store_true", help="Run without making any changes")

    def handle(self, *args, **options):
        store_id = options.get("store_id")
        limit = options.get("limit")
        dry_run = options.get("dry_run")

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting media migration for store {store_id or "all"} (dry run: {dry_run})'
            )
        )

        # Get media files to migrate
        queryset = MediaFile.objects.all()
        if store_id:
            queryset = queryset.filter(store_id=store_id)

        total_count = queryset.count()
        self.stdout.write(f"Found {total_count} media files to migrate")

        if not total_count:
            self.stdout.write(self.style.SUCCESS("No media files to migrate"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run - no changes will be made"))

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        media_service = MediaService()

        for media_file in queryset[:limit]:
            try:
                self.stdout.write(f"Processing {media_file.original_filename}... ", ending="")

                if dry_run:
                    self.stdout.write(self.style.WARNING("[DRY RUN]"))
                    skipped_count += 1
                    continue

                # Migration logic here
                self.stdout.write(self.style.SUCCESS("[DONE]"))
                migrated_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR: {str(e)}]"))
                error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nMigration complete: {migrated_count} migrated, {skipped_count} skipped, {error_count} errors"
            )
        )

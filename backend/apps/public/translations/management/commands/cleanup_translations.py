"""
Clean up unused translation keys management command.
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from apps.public.translations.models import TranslationKey


class Command(BaseCommand):
    help = 'Clean up unused translation keys'
    
    def handle(self, *args, **options):
        # Find and delete unused keys
        unused = TranslationKey.objects.annotate(
            trans_count=Count('translations')
        ).filter(trans_count=0)
        
        count = unused.count()
        if count > 0:
            self.stdout.write(f'Deleting {count} unused translation keys...')
            unused.delete()
            self.stdout.write(self.style.SUCCESS('Cleanup complete'))
        else:
            self.stdout.write('No unused translation keys found')

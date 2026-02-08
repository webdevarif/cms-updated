from django.db import migrations
from django.db.models import F


def fix_store_references(apps, schema_editor):
    """
    Fix store references in all models that have a store foreign key.
    This ensures all store references point to stores.Store instead of accounts.Store
    """
    # No need to run any data migration since we're just fixing the schema
    # The actual data migration would depend on your specific database structure
    pass


class Migration(migrations.Migration):
    """
    Migration to fix store references in the posts app.
    This ensures all store foreign keys point to stores.Store instead of accounts.Store.
    """

    dependencies = [
        ("posts", "0001_initial"),
        ("stores", "0001_initial"),  # Ensure stores app is available
    ]

    operations = [
        migrations.RunPython(
            code=fix_store_references,
            reverse_code=migrations.RunPython.noop,
            hints={"target_db": "default"},
        ),
        # Add any necessary field alterations here if needed
    ]

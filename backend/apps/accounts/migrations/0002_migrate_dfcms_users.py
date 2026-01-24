"""
Migrate DFCMS users to new accounts models.
"""
from django.db import migrations


def migrate_global_users(apps, schema_editor):
    """Migrate DFCMS GlobalUser to new User model"""
    # Try to get DFCMS GlobalUser model (may not exist in fresh install)
    try:
        GlobalUser = apps.get_model('modules', 'GlobalUser')
        Store = apps.get_model('stores', 'Store')
        User = apps.get_model('accounts', 'User')
        
        for global_user in GlobalUser.objects.all():
            # Create user for each store they belong to
            for store in global_user.stores.all():
                User.objects.create(
                    email=global_user.email,
                    username=global_user.username,
                    first_name=global_user.first_name,
                    last_name=global_user.last_name,
                    is_verified=global_user.is_verified,
                    is_active=global_user.is_active,
                    is_staff=global_user.is_staff,
                    is_superuser=global_user.is_superuser,
                    created_at=global_user.date_joined,
                )
    except LookupError:
        # DFCMS modules app doesn't exist - skip migration
        pass


def migrate_store_users(apps, schema_editor):
    """Migrate DFCMS UserAccount to new User model"""
    # Try to get DFCMS UserAccount model (may not exist in fresh install)
    try:
        UserAccount = apps.get_model('modules', 'UserAccount')
        Store = apps.get_model('stores', 'Store')
        User = apps.get_model('accounts', 'User')
        StoreUser = apps.get_model('accounts', 'StoreUser')
        
        for store_user in UserAccount.objects.all():
            # Create or get global user
            user, created = User.objects.get_or_create(
                email=store_user.email,
                defaults={
                    'username': store_user.username,
                    'first_name': store_user.first_name,
                    'last_name': store_user.last_name,
                    'is_verified': store_user.is_verified,
                    'is_active': store_user.is_active,
                    'is_staff': store_user.is_staff,
                    'created_at': store_user.date_joined,
                }
            )
            
            # Create store user relationship
            StoreUser.objects.get_or_create(
                user=user,
                store=store_user.store,
                defaults={
                    'role': getattr(store_user, 'role', 'customer'),
                    'is_active': store_user.is_active,
                }
            )
    except LookupError:
        # DFCMS modules app doesn't exist - skip migration
        pass


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
        ('stores', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(migrate_global_users),
        migrations.RunPython(migrate_store_users),
    ]
